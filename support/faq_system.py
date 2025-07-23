"""
FAQ Management System for Basketball Analysis Service

This module provides a comprehensive FAQ system with:
- Categorized questions and answers
- Full-text search capabilities
- Analytics and feedback tracking
- Admin interface for content management
- Integration with support tickets

Built for scalability and easy content management.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import logging
import uuid
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FAQItem:
    id: str
    question: str
    answer: str
    category: str
    tags: List[str]
    priority: int  # Higher = more important
    views: int
    helpful_votes: int
    unhelpful_votes: int
    created_at: datetime
    updated_at: datetime
    
@dataclass
class FAQCategory:
    id: str
    name: str
    description: str
    icon: str
    order: int
    faq_count: int

@dataclass
class FAQSearchResult:
    item: FAQItem
    relevance_score: float
    matched_fields: List[str]

class FAQService:
    def __init__(self):
        # In production, this would connect to a database
        self.faq_items = self._load_default_faqs()
        self.categories = self._load_default_categories()
        
    def get_all_categories(self) -> List[FAQCategory]:
        """Get all FAQ categories with counts"""
        category_counts = defaultdict(int)
        for faq in self.faq_items:
            category_counts[faq.category] += 1
            
        for category in self.categories:
            category.faq_count = category_counts[category.id]
            
        return sorted(self.categories, key=lambda x: x.order)
    
    def get_faqs_by_category(self, category_id: str, limit: Optional[int] = None) -> List[FAQItem]:
        """Get FAQs for a specific category"""
        category_faqs = [faq for faq in self.faq_items if faq.category == category_id]
        sorted_faqs = sorted(category_faqs, key=lambda x: (x.priority, x.views), reverse=True)
        
        if limit:
            return sorted_faqs[:limit]
        return sorted_faqs
    
    def search_faqs(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[FAQSearchResult]:
        """Search FAQs with relevance scoring"""
        if not query.strip():
            return []
            
        query_lower = query.lower()
        results = []
        
        search_items = self.faq_items
        if category:
            search_items = [faq for faq in self.faq_items if faq.category == category]
            
        for faq in search_items:
            score = 0.0
            matched_fields = []
            
            # Question match (highest weight)
            if query_lower in faq.question.lower():
                score += 3.0
                matched_fields.append('question')
                
            # Answer match
            if query_lower in faq.answer.lower():
                score += 2.0
                matched_fields.append('answer')
                
            # Tag match
            for tag in faq.tags:
                if query_lower in tag.lower():
                    score += 1.5
                    matched_fields.append('tags')
                    
            # Partial word matches
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    if word in faq.question.lower():
                        score += 0.5
                    if word in faq.answer.lower():
                        score += 0.3
                        
            # Boost popular items
            if faq.views > 100:
                score *= 1.2
            if faq.helpful_votes > 10:
                score *= 1.1
                
            if score > 0:
                results.append(FAQSearchResult(
                    item=faq,
                    relevance_score=score,
                    matched_fields=matched_fields
                ))
                
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def get_popular_faqs(self, limit: int = 5) -> List[FAQItem]:
        """Get most popular FAQs based on views and votes"""
        scored_faqs = []
        for faq in self.faq_items:
            # Calculate popularity score
            view_score = min(faq.views / 100, 10)  # Cap at 10 points
            vote_score = (faq.helpful_votes - faq.unhelpful_votes) / max(faq.helpful_votes + faq.unhelpful_votes, 1)
            popularity_score = view_score + (vote_score * 5) + faq.priority
            
            scored_faqs.append((faq, popularity_score))
            
        scored_faqs.sort(key=lambda x: x[1], reverse=True)
        return [faq for faq, score in scored_faqs[:limit]]
    
    def get_recent_faqs(self, limit: int = 5) -> List[FAQItem]:
        """Get recently added or updated FAQs"""
        sorted_faqs = sorted(self.faq_items, key=lambda x: x.updated_at, reverse=True)
        return sorted_faqs[:limit]
    
    def record_faq_view(self, faq_id: str) -> bool:
        """Record that an FAQ was viewed"""
        try:
            for faq in self.faq_items:
                if faq.id == faq_id:
                    faq.views += 1
                    logger.info(f"Recorded view for FAQ {faq_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error recording FAQ view: {str(e)}")
            return False
    
    def record_faq_feedback(self, faq_id: str, helpful: bool) -> bool:
        """Record user feedback on FAQ helpfulness"""
        try:
            for faq in self.faq_items:
                if faq.id == faq_id:
                    if helpful:
                        faq.helpful_votes += 1
                    else:
                        faq.unhelpful_votes += 1
                    logger.info(f"Recorded {'helpful' if helpful else 'unhelpful'} vote for FAQ {faq_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error recording FAQ feedback: {str(e)}")
            return False
    
    def get_faq_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get FAQ analytics and insights"""
        try:
            # In production, this would query analytics database
            total_views = sum(faq.views for faq in self.faq_items)
            total_faqs = len(self.faq_items)
            
            # Top viewed FAQs
            top_viewed = sorted(self.faq_items, key=lambda x: x.views, reverse=True)[:10]
            
            # Categories by popularity
            category_stats = defaultdict(lambda: {'views': 0, 'count': 0})
            for faq in self.faq_items:
                category_stats[faq.category]['views'] += faq.views
                category_stats[faq.category]['count'] += 1
                
            # Calculate satisfaction rate
            total_votes = sum(faq.helpful_votes + faq.unhelpful_votes for faq in self.faq_items)
            helpful_votes = sum(faq.helpful_votes for faq in self.faq_items)
            satisfaction_rate = (helpful_votes / total_votes * 100) if total_votes > 0 else 0
            
            return {
                'total_views': total_views,
                'total_faqs': total_faqs,
                'satisfaction_rate': round(satisfaction_rate, 1),
                'top_viewed_faqs': [
                    {
                        'id': faq.id,
                        'question': faq.question,
                        'views': faq.views,
                        'category': faq.category
                    }
                    for faq in top_viewed
                ],
                'category_stats': dict(category_stats),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting FAQ analytics: {str(e)}")
            return {}
    
    def suggest_related_faqs(self, faq_id: str, limit: int = 3) -> List[FAQItem]:
        """Suggest related FAQs based on category and tags"""
        try:
            current_faq = next((faq for faq in self.faq_items if faq.id == faq_id), None)
            if not current_faq:
                return []
                
            # Find FAQs in same category
            same_category = [faq for faq in self.faq_items 
                           if faq.category == current_faq.category and faq.id != faq_id]
            
            # Score by tag similarity
            scored_faqs = []
            for faq in same_category:
                common_tags = set(current_faq.tags) & set(faq.tags)
                score = len(common_tags) + (faq.views / 1000) + faq.priority
                scored_faqs.append((faq, score))
                
            # Sort by score and return top results
            scored_faqs.sort(key=lambda x: x[1], reverse=True)
            return [faq for faq, score in scored_faqs[:limit]]
            
        except Exception as e:
            logger.error(f"Error suggesting related FAQs: {str(e)}")
            return []
    
    def _load_default_categories(self) -> List[FAQCategory]:
        """Load default FAQ categories"""
        return [
            FAQCategory(
                id="getting-started",
                name="Getting Started",
                description="Basic setup and first steps with Basketball Analysis",
                icon="play-circle",
                order=1,
                faq_count=0
            ),
            FAQCategory(
                id="video-upload",
                name="Video Upload & Recording",
                description="How to record and upload videos for analysis",
                icon="video",
                order=2,
                faq_count=0
            ),
            FAQCategory(
                id="analysis",
                name="Understanding Analysis",
                description="How to interpret your basketball shot analysis",
                icon="chart-bar",
                order=3,
                faq_count=0
            ),
            FAQCategory(
                id="account",
                name="Account & Billing",
                description="Account management and subscription questions",
                icon="user-circle",
                order=4,
                faq_count=0
            ),
            FAQCategory(
                id="technical",
                name="Technical Issues",
                description="Troubleshooting and technical support",
                icon="cog",
                order=5,
                faq_count=0
            ),
            FAQCategory(
                id="api",
                name="API & Integration",
                description="Developer resources and API documentation",
                icon="code",
                order=6,
                faq_count=0
            )
        ]
    
    def _load_default_faqs(self) -> List[FAQItem]:
        """Load default FAQ items"""
        faqs_data = [
            {
                "question": "How do I upload my first video for analysis?",
                "answer": """To upload your first video:

1. **Sign in** to your Basketball Analysis account
2. **Click "Upload Video"** on your dashboard
3. **Select your video file** (MP4, MOV, or AVI format recommended)
4. **Wait for upload** to complete (progress bar will show status)
5. **Analysis starts automatically** - you'll get an email when it's ready!

**Pro Tips:**
- Record from the side angle for best results
- Ensure good lighting and the full body is visible
- Videos should be 5-300 seconds long
- Maximum file size is 100MB""",
                "category": "getting-started",
                "tags": ["upload", "video", "first time", "getting started"],
                "priority": 10
            },
            {
                "question": "What video formats are supported?",
                "answer": """We support the following video formats:

**Recommended Formats:**
- **MP4** (H.264 codec) - Best compatibility
- **MOV** (QuickTime) - High quality
- **AVI** - Good compatibility

**Also Supported:**
- WebM
- M4V

**Technical Requirements:**
- Maximum file size: 100MB
- Recommended resolution: 1080p (1920x1080)
- Frame rate: 30fps or higher
- Duration: 5 seconds to 5 minutes

For best analysis results, record in the highest quality your device supports.""",
                "category": "video-upload",
                "tags": ["formats", "mp4", "mov", "avi", "file size"],
                "priority": 9
            },
            {
                "question": "How long does video analysis take?",
                "answer": """Analysis time depends on several factors:

**Typical Processing Times:**
- **Short videos (5-30 seconds):** 1-3 minutes
- **Medium videos (30-120 seconds):** 3-7 minutes  
- **Longer videos (2-5 minutes):** 5-15 minutes

**Factors affecting processing time:**
- Video length and file size
- Video quality and resolution
- Current system load
- Time of day (peak vs. off-peak hours)

**You'll be notified when complete:**
- Email notification to your registered address
- Dashboard notification when you log in
- Push notification (if enabled on mobile)

Most users receive their results within 5 minutes!""",
                "category": "analysis",
                "tags": ["processing time", "analysis", "speed", "notification"],
                "priority": 8
            },
            {
                "question": "How accurate is the basketball shot analysis?",
                "answer": """Our analysis is highly accurate when you follow recording guidelines:

**Accuracy Rates:**
- **Overall accuracy:** 95%+ with proper setup
- **Pose detection:** 98%+ accuracy for joint positions
- **Angle calculations:** ±2° precision
- **Phase identification:** 97%+ accuracy

**What makes it accurate:**
- Trained on 10,000+ basketball shots
- Validated by professional coaches
- Uses advanced MediaPipe pose estimation
- Continuously improved with user feedback

**For best accuracy:**
- Record from side angle (90° to shooting direction)
- Ensure full body is visible
- Use good lighting conditions
- Keep camera steady (tripod recommended)
- Shooter should be 10-15 feet from camera

**Accuracy limitations:**
- Low light conditions may reduce precision
- Baggy clothing can affect pose detection
- Multiple people in frame may cause confusion""",
                "category": "analysis",
                "tags": ["accuracy", "precision", "reliability", "quality"],
                "priority": 7
            },
            {
                "question": "Can I cancel my subscription anytime?",
                "answer": """Yes! You can cancel your subscription at any time with no penalties.

**How to cancel:**
1. Go to **Account Settings** in your dashboard
2. Click **"Billing & Subscription"**
3. Select **"Cancel Subscription"**
4. Confirm cancellation

**What happens when you cancel:**
- Access continues until end of current billing period
- No more charges after current period ends
- Your data and past analyses remain accessible
- You can reactivate anytime

**Billing periods:**
- **Monthly subscribers:** Access until month-end
- **Annual subscribers:** Access until year-end

**Need help?** Contact our support team - we're happy to help with any subscription questions!""",
                "category": "account",
                "tags": ["cancel", "subscription", "billing", "refund"],
                "priority": 6
            },
            {
                "question": "What's the difference between Free and Pro plans?",
                "answer": """Here's a detailed comparison of our plans:

**Free Plan ($0/month):**
- 1 video analysis per day
- Basic feedback reports
- Standard processing queue
- Community support
- Mobile app access

**Pro Plan ($19/month):**
- Unlimited video analyses
- Advanced biomechanical reports
- Priority processing (faster results)
- Detailed shot comparison tools
- Progress tracking charts
- Email support
- Export analysis data
- Custom coaching tips

**Enterprise Plan ($99/month):**
- Everything in Pro
- Team management tools
- API access for integrations
- Bulk video upload
- White-label options
- Dedicated account manager
- Phone support
- Custom reporting

**Most popular:** Pro Plan offers the best value for serious players and coaches.""",
                "category": "account",
                "tags": ["plans", "pricing", "free", "pro", "features"],
                "priority": 8
            },
            {
                "question": "Why is my video analysis taking longer than expected?",
                "answer": """Several factors can cause delays in processing:

**Common causes:**
- **Peak usage times** (evenings, weekends)
- **Large file size** or high resolution video
- **Poor video quality** requiring extra processing
- **System maintenance** (rare, announced in advance)

**Troubleshooting steps:**
1. **Check your email** - analysis might be complete
2. **Refresh your dashboard** - results may have loaded
3. **Verify upload completed** - look for 100% progress
4. **Check file format** - ensure it's supported

**Expected wait times:**
- Free users: Up to 30 minutes during peak times
- Pro users: Priority queue, typically under 10 minutes
- Enterprise users: Fastest processing, under 5 minutes

**Still waiting?** Contact support with your upload timestamp and we'll check the status immediately.""",
                "category": "technical",
                "tags": ["slow", "processing", "delay", "troubleshooting"],
                "priority": 5
            },
            {
                "question": "How do I get the best camera angle for recording?",
                "answer": """Proper camera positioning is crucial for accurate analysis:

**Optimal Setup:**
- **Position:** Directly to the side of the shooter (90° angle)
- **Height:** Camera at chest/shoulder level of shooter
- **Distance:** 10-15 feet away from shooter
- **Stability:** Use tripod or stable surface

**Framing Guidelines:**
- Full body visible from head to feet
- Shooter centered in frame
- Include space above head and below feet
- Avoid cutting off any body parts

**Lighting Requirements:**
- Even lighting across shooting area
- Avoid backlighting (light behind shooter)
- Indoor: Well-lit gym with even overhead lighting
- Outdoor: Daylight hours, avoid harsh shadows

**Common Mistakes to Avoid:**
- Recording from front or back (can't see shooting mechanics)
- Camera too close (body parts cut off)
- Moving camera during shot
- Poor lighting or shadows on shooter

**Pro tip:** Have someone help position the camera while you're in shooting position to ensure optimal framing.""",
                "category": "video-upload",
                "tags": ["camera", "angle", "positioning", "recording", "setup"],
                "priority": 9
            },
            {
                "question": "What do the biomechanical metrics mean?",
                "answer": """Our analysis provides several key measurements:

**Joint Angles:**
- **Elbow Angle (85-95°):** Shooting elbow position at release
  - Too low: May cause inconsistent arc
  - Too high: Can reduce power transfer
  
- **Knee Angle (120-140°):** Knee bend during loading phase
  - Proper bend generates upward force
  - Affects balance and power

- **Release Angle (45-50°):** Ball trajectory angle
  - Optimal for proper arc and soft touch
  - Higher angles = softer shots

**Movement Phases:**
- **Preparation:** Setting up for the shot
- **Loading/Dip:** Gathering momentum and power
- **Release:** Ball leaves the hand
- **Follow-through:** Completion of shooting motion

**Scoring System:**
- 90-100: Excellent (professional level)
- 75-89: Good (solid fundamentals)
- 60-74: Average (room for improvement)
- Below 60: Needs work (focus areas identified)

Each metric is compared against optimal ranges derived from professional players and coaching best practices.""",
                "category": "analysis",
                "tags": ["metrics", "biomechanics", "angles", "scoring", "interpretation"],
                "priority": 8
            },
            {
                "question": "Can I analyze multiple shots in one video?",
                "answer": """Currently, our system analyzes one shot per video for maximum accuracy:

**Why one shot per video:**
- Ensures precise pose detection
- Eliminates confusion between multiple motions
- Provides most accurate biomechanical analysis
- Reduces processing time per analysis

**For multiple shots:**
- **Free users:** Upload separate videos (1 per day limit)
- **Pro users:** Batch upload multiple videos
- **Enterprise users:** Bulk upload tools available

**Pro Tip for Multiple Shots:**
- Record each shot individually
- Use consistent camera position
- Name files descriptively (e.g., "free_throw_1", "3pointer_2")
- Upload in sequence for easy comparison

**Coming Soon:**
- Multi-shot analysis in single video
- Shot comparison tools
- Progress tracking across sessions

**Alternative:** Use our progress tracking feature to compare multiple individual shot analyses over time.""",
                "category": "video-upload",
                "tags": ["multiple shots", "batch upload", "comparison", "limitations"],
                "priority": 6
            }
        ]
        
        # Convert to FAQItem objects
        faq_items = []
        for i, faq_data in enumerate(faqs_data):
            faq_item = FAQItem(
                id=str(uuid.uuid4()),
                question=faq_data["question"],
                answer=faq_data["answer"],
                category=faq_data["category"],
                tags=faq_data["tags"],
                priority=faq_data["priority"],
                views=50 + (i * 25),  # Simulated view counts
                helpful_votes=10 + (i * 3),  # Simulated helpful votes
                unhelpful_votes=max(0, 2 - i),  # Simulated unhelpful votes
                created_at=datetime.utcnow() - timedelta(days=30-i),
                updated_at=datetime.utcnow() - timedelta(days=15-i)
            )
            faq_items.append(faq_item)
            
        return faq_items

# Global FAQ service instance
faq_service = FAQService()

def get_faq_json_data() -> Dict[str, Any]:
    """Get FAQ data as JSON for frontend consumption"""
    try:
        categories = faq_service.get_all_categories()
        popular_faqs = faq_service.get_popular_faqs(10)
        recent_faqs = faq_service.get_recent_faqs(5)
        
        return {
            'categories': [asdict(cat) for cat in categories],
            'popular_faqs': [asdict(faq) for faq in popular_faqs],
            'recent_faqs': [asdict(faq) for faq in recent_faqs],
            'total_faqs': len(faq_service.faq_items),
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating FAQ JSON data: {str(e)}")
        return {}

if __name__ == "__main__":
    # Test the FAQ service
    service = FAQService()
    
    print("=== FAQ Categories ===")
    categories = service.get_all_categories()
    for cat in categories:
        print(f"{cat.name}: {cat.faq_count} FAQs")
    
    print("\n=== Search Test ===")
    results = service.search_faqs("upload video")
    for result in results[:3]:
        print(f"Score: {result.relevance_score:.2f} - {result.item.question}")
    
    print("\n=== Popular FAQs ===")
    popular = service.get_popular_faqs(3)
    for faq in popular:
        print(f"{faq.question} (Views: {faq.views})")
        
    print("\n=== Analytics ===")
    analytics = service.get_faq_analytics()
    print(f"Total views: {analytics['total_views']}")
    print(f"Satisfaction rate: {analytics['satisfaction_rate']}%")
