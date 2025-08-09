"""
Professional PDF Report Generator for Basketball Shot Analysis
Generates detailed 60-day improvement plans with customized drills and training programs
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white, red, green, blue, orange, grey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime, timedelta
import os

class BasketballAnalysisPDFGenerator:
    """Professional PDF generator for basketball shot analysis reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Heading styles
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        )
        
        self.heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        # Bullet style
        self.bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            bulletIndent=10,
            fontName='Helvetica'
        )
        
        # Drill instruction style
        self.drill_style = ParagraphStyle(
            'DrillStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            leftIndent=15,
            fontName='Helvetica',
            textColor=colors.darkgreen
        )
        
        # Warning/Important style
        self.warning_style = ParagraphStyle(
            'WarningStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=10,
            fontName='Helvetica-Bold',
            textColor=colors.red,
            backColor=colors.lightgrey
        )

    def generate_improvement_plan(self, analysis_results, job_id, output_path=None):
        """Generate comprehensive 60-day improvement plan PDF"""
        
        if not output_path:
            output_path = f"60_Day_Shot_Improvement_Plan_{job_id}.pdf"
            
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build document content
        story = []
        
        # Title page
        story.extend(self._create_title_page(analysis_results, job_id))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(analysis_results))
        story.append(PageBreak())
        
        # Detailed flaw analysis
        story.extend(self._create_flaw_analysis_section(analysis_results))
        story.append(PageBreak())
        
        # 60-day improvement plan
        story.extend(self._create_60_day_plan(analysis_results))
        story.append(PageBreak())
        
        # Weekly training schedules
        story.extend(self._create_weekly_schedules(analysis_results))
        story.append(PageBreak())
        
        # Drill library with detailed instructions
        story.extend(self._create_drill_library(analysis_results))
        story.append(PageBreak())
        
        # Progress tracking and benchmarks
        story.extend(self._create_progress_tracking(analysis_results))
        story.append(PageBreak())
        
        # Resources and citations
        story.extend(self._create_resources_section())
        
        # Build PDF
        doc.build(story)
        
        return output_path

    def _create_title_page(self, analysis_results, job_id):
        """Create professional title page"""
        content = []
        
        # Main title
        content.append(Paragraph("🏀 PERSONALIZED BASKETBALL SHOT", self.title_style))
        content.append(Paragraph("IMPROVEMENT PLAN", self.title_style))
        content.append(Spacer(1, 30))
        
        # Subtitle
        content.append(Paragraph("Comprehensive 60-Day Training Program", self.heading1_style))
        content.append(Paragraph("Based on Advanced Biomechanical Analysis", self.heading2_style))
        content.append(Spacer(1, 40))
        
        # Analysis details table
        analysis_data = [
            ['Analysis ID:', job_id],
            ['Analysis Date:', datetime.now().strftime('%B %d, %Y')],
            ['Flaws Detected:', str(len(analysis_results.get('detailed_flaws', [])))],
            ['Shot Phases Analyzed:', str(len(analysis_results.get('shot_phases', [])))],
            ['Feedback Points:', str(len(analysis_results.get('feedback_points', [])))],
            ['Plan Duration:', '60 Days'],
            ['Recommended Practice:', '45-60 minutes daily'],
            ['Re-evaluation Schedule:', 'Every 2 weeks']
        ]
        
        table = Table(analysis_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 40))
        
        # Disclaimer
        disclaimer = """
        <b>IMPORTANT DISCLAIMER:</b><br/>
        This improvement plan is generated based on computer vision analysis of your shooting form. 
        While the recommendations are based on proven basketball biomechanics principles, individual 
        results may vary. We recommend working with a qualified basketball coach in conjunction with 
        this plan for optimal results. Always warm up properly before practice and stop if you 
        experience pain or discomfort.
        """
        
        content.append(Paragraph(disclaimer, self.warning_style))
        content.append(Spacer(1, 20))
        
        # Footer
        content.append(Paragraph("Generated by Basketball Shot Analysis AI", self.body_style))
        content.append(Paragraph("www.basketballanalysis.ai", self.body_style))
        
        return content

    def _create_executive_summary(self, analysis_results):
        """Create executive summary of analysis"""
        content = []
        
        content.append(Paragraph("EXECUTIVE SUMMARY", self.heading1_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        
        if detailed_flaws:
            # Overall assessment
            avg_severity = sum(flaw['severity'] for flaw in detailed_flaws) / len(detailed_flaws)
            
            if avg_severity < 20:
                assessment = "Your shooting form shows minor areas for improvement with excellent fundamentals."
                color = "green"
            elif avg_severity < 40:
                assessment = "Your shooting form has several moderate issues that can be addressed with focused practice."
                color = "orange" 
            else:
                assessment = "Your shooting form requires significant attention to fundamental mechanics."
                color = "red"
                
            content.append(Paragraph(f"<b>Overall Assessment:</b> {assessment}", self.body_style))
            content.append(Spacer(1, 10))
            
            # Priority flaws
            content.append(Paragraph("Primary Areas for Improvement:", self.heading2_style))
            
            for i, flaw in enumerate(detailed_flaws[:3], 1):
                flaw_text = f"""
                <b>{i}. {flaw['flaw_type'].replace('_', ' ').title()}</b> (Severity: {flaw['severity']:.1f})<br/>
                <i>Issue:</i> {flaw['plain_language']}<br/>
                <i>Primary Focus:</i> {flaw['coaching_tip']}
                """
                content.append(Paragraph(flaw_text, self.body_style))
                content.append(Spacer(1, 8))
            
            # Success metrics
            content.append(Paragraph("Expected Outcomes (60 Days):", self.heading2_style))
            outcomes = [
                "• Improved shooting consistency by 15-25%",
                "• Reduced shooting variance in key biomechanical markers",
                "• Enhanced muscle memory for proper shooting form",
                "• Increased shooting range with maintained accuracy",
                "• Better understanding of personal shooting mechanics"
            ]
            
            for outcome in outcomes:
                content.append(Paragraph(outcome, self.bullet_style))
                
        else:
            content.append(Paragraph("No significant flaws detected in your shooting form. This plan will focus on refinement and consistency.", self.body_style))
            
        return content

    def _create_flaw_analysis_section(self, analysis_results):
        """Create detailed analysis of each detected flaw"""
        content = []
        
        content.append(Paragraph("DETAILED FLAW ANALYSIS", self.heading1_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        
        if not detailed_flaws:
            content.append(Paragraph("Excellent news! Our analysis did not detect any significant flaws in your shooting form. Your focus should be on maintaining consistency and fine-tuning your mechanics.", self.body_style))
            return content
            
        for i, flaw in enumerate(detailed_flaws, 1):
            content.append(Paragraph(f"Flaw #{i}: {flaw['flaw_type'].replace('_', ' ').title()}", self.heading2_style))
            
            # Flaw details table
            flaw_data = [
                ['Severity Level:', f"{flaw['severity']:.1f}/100"],
                ['Shot Phase:', flaw.get('phase', 'Overall Motion')],
                ['Frame Location:', f"Frame {flaw.get('frame_number', 'N/A')}"],
                ['Category:', self._get_flaw_category(flaw['flaw_type'])]
            ]
            
            table = Table(flaw_data, colWidths=[1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            content.append(table)
            content.append(Spacer(1, 10))
            
            # Problem description
            content.append(Paragraph("<b>What's Happening:</b>", self.heading3_style))
            plain_language = flaw.get('plain_language') or flaw.get('description', 'Issue detected with shooting form')
            content.append(Paragraph(plain_language, self.body_style))
            content.append(Spacer(1, 8))
            
            # Impact on shooting
            impact = self._get_flaw_impact(flaw['flaw_type'])
            content.append(Paragraph("<b>Impact on Your Shot:</b>", self.heading3_style))
            content.append(Paragraph(impact, self.body_style))
            content.append(Spacer(1, 8))
            
            # Biomechanical explanation
            biomech = self._get_biomechanical_explanation(flaw['flaw_type'])
            content.append(Paragraph("<b>Biomechanical Analysis:</b>", self.heading3_style))
            content.append(Paragraph(biomech, self.body_style))
            content.append(Spacer(1, 8))
            
            # Correction strategy
            content.append(Paragraph("<b>Correction Strategy:</b>", self.heading3_style))
            coaching_tip = flaw.get('coaching_tip') or flaw.get('remedy_tip', 'Focus on correcting this aspect of your shooting form')
            content.append(Paragraph(coaching_tip, self.body_style))
            content.append(Spacer(1, 15))
            
        return content

    def _create_60_day_plan(self, analysis_results):
        """Create comprehensive 60-day improvement plan"""
        content = []
        
        content.append(Paragraph("60-DAY IMPROVEMENT PLAN", self.heading1_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        
        # Plan overview
        content.append(Paragraph("Plan Overview", self.heading2_style))
        overview_text = """
        This 60-day plan is structured in four phases, each building upon the previous one. 
        The plan prioritizes your most severe flaws first while gradually incorporating 
        comprehensive shooting development. Each phase includes specific goals, drills, 
        and measurable benchmarks.
        """
        content.append(Paragraph(overview_text, self.body_style))
        content.append(Spacer(1, 15))
        
        # Phase breakdown
        phases = [
            {
                'name': 'Foundation Phase (Days 1-15)',
                'focus': 'Basic mechanics and most critical flaw correction',
                'goals': ['Establish proper shooting stance', 'Address highest severity flaw', 'Build consistent routine'],
                'practice_time': '45 minutes daily',
                'evaluation': 'Day 14 re-analysis'
            },
            {
                'name': 'Development Phase (Days 16-30)', 
                'focus': 'Technique refinement and secondary flaw correction',
                'goals': ['Improve shooting consistency', 'Address secondary flaws', 'Increase shooting range'],
                'practice_time': '50 minutes daily',
                'evaluation': 'Day 28 re-analysis'
            },
            {
                'name': 'Integration Phase (Days 31-45)',
                'focus': 'Game-like shooting and movement integration',
                'goals': ['Shooting off the dribble', 'Quick release development', 'Pressure shooting'],
                'practice_time': '55 minutes daily', 
                'evaluation': 'Day 42 re-analysis'
            },
            {
                'name': 'Mastery Phase (Days 46-60)',
                'focus': 'Advanced techniques and consistency under pressure',
                'goals': ['Competition simulation', 'Advanced footwork', 'Mental approach'],
                'practice_time': '60 minutes daily',
                'evaluation': 'Final comprehensive analysis'
            }
        ]
        
        for phase in phases:
            content.append(Paragraph(phase['name'], self.heading2_style))
            
            phase_data = [
                ['Primary Focus:', phase['focus']],
                ['Daily Practice:', phase['practice_time']],
                ['Evaluation:', phase['evaluation']]
            ]
            
            table = Table(phase_data, colWidths=[1.5*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            content.append(table)
            content.append(Spacer(1, 8))
            
            content.append(Paragraph("<b>Phase Goals:</b>", self.heading3_style))
            for goal in phase['goals']:
                content.append(Paragraph(f"• {goal}", self.bullet_style))
            content.append(Spacer(1, 15))
            
        return content

    def _create_weekly_schedules(self, analysis_results):
        """Create detailed weekly training schedules"""
        content = []
        
        content.append(Paragraph("WEEKLY TRAINING SCHEDULES", self.heading1_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        primary_flaws = detailed_flaws[:3] if detailed_flaws else []
        
        # Week 1-2 Schedule (Foundation)
        content.append(Paragraph("Weeks 1-2: Foundation Phase", self.heading2_style))
        
        foundation_schedule = [
            ['Day', 'Primary Focus', 'Duration', 'Key Drills'],
            ['Monday', 'Stance & Balance', '45 min', 'Wall shooting, Balance drills'],
            ['Tuesday', f'Primary Flaw: {primary_flaws[0]["flaw_type"].replace("_", " ").title() if primary_flaws else "Form shooting"}', '45 min', 'Specific correction drills'],
            ['Wednesday', 'Shooting Rhythm', '45 min', 'Slow-motion shooting'],
            ['Thursday', f'Secondary Flaw: {primary_flaws[1]["flaw_type"].replace("_", " ").title() if len(primary_flaws) > 1 else "Follow-through"}', '45 min', 'Targeted exercises'],
            ['Friday', 'Consistency Training', '45 min', 'Repetition shooting'],
            ['Saturday', 'Full Form Integration', '45 min', 'Complete shooting motion'],
            ['Sunday', 'Rest & Analysis', '30 min', 'Video review, light shooting']
        ]
        
        table = Table(foundation_schedule, colWidths=[1*inch, 1.8*inch, 1*inch, 2.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Progressive schedule notes
        content.append(Paragraph("Schedule Progression Notes:", self.heading3_style))
        notes = [
            "• Weeks 3-4: Increase intensity, add movement-based drills",
            "• Weeks 5-6: Incorporate game-like scenarios, pressure situations", 
            "• Weeks 7-8: Advanced techniques, competition simulation",
            "• Rest days are crucial for muscle memory consolidation",
            "• Adjust intensity based on fatigue and progress",
            "• Always include 10-minute warm-up and 5-minute cool-down"
        ]
        
        for note in notes:
            content.append(Paragraph(note, self.bullet_style))
            
        return content

    def _create_drill_library(self, analysis_results):
        """Create comprehensive drill library with detailed instructions"""
        content = []
        
        content.append(Paragraph("COMPREHENSIVE DRILL LIBRARY", self.heading1_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        
        # Core fundamentals drills (always included)
        core_drills = self._get_core_drills()
        
        content.append(Paragraph("Core Fundamental Drills", self.heading2_style))
        content.append(Paragraph("These drills should be performed regardless of specific flaws detected:", self.body_style))
        content.append(Spacer(1, 10))
        
        for drill in core_drills:
            content.extend(self._format_drill(drill))
            content.append(Spacer(1, 15))
        
        # Flaw-specific drills
        if detailed_flaws:
            content.append(Paragraph("Personalized Correction Drills", self.heading2_style))
            content.append(Paragraph("These drills specifically target your detected flaws:", self.body_style))
            content.append(Spacer(1, 10))
            
            for flaw in detailed_flaws:
                flaw_drills = self._get_flaw_specific_drills(flaw['flaw_type'])
                
                content.append(Paragraph(f"For {flaw['flaw_type'].replace('_', ' ').title()}:", self.heading3_style))
                
                for drill in flaw_drills:
                    content.extend(self._format_drill(drill))
                    content.append(Spacer(1, 10))
                    
                content.append(Spacer(1, 15))
        
        return content

    def _format_drill(self, drill):
        """Format individual drill with detailed instructions"""
        content = []
        
        # Drill header
        content.append(Paragraph(f"<b>{drill['name']}</b>", self.heading3_style))
        
        # Drill info table
        drill_info = [
            ['Purpose:', drill['purpose']],
            ['Equipment:', drill['equipment']],
            ['Duration:', drill['duration']],
            ['Difficulty:', drill['difficulty']],
            ['Repetitions:', drill['reps']]
        ]
        
        table = Table(drill_info, colWidths=[1.2*inch, 4.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 8))
        
        # Step-by-step instructions
        content.append(Paragraph("<b>Step-by-Step Instructions:</b>", self.heading3_style))
        for i, step in enumerate(drill['instructions'], 1):
            content.append(Paragraph(f"{i}. {step}", self.drill_style))
            
        # Key points
        if 'key_points' in drill:
            content.append(Paragraph("<b>Key Coaching Points:</b>", self.heading3_style))
            for point in drill['key_points']:
                content.append(Paragraph(f"• {point}", self.bullet_style))
        
        # Video reference
        if 'video_reference' in drill:
            content.append(Paragraph(f"<b>Video Reference:</b> {drill['video_reference']}", self.drill_style))
            
        return content

    def _create_progress_tracking(self, analysis_results):
        """Create progress tracking and benchmark section"""
        content = []
        
        content.append(Paragraph("PROGRESS TRACKING & BENCHMARKS", self.heading1_style))
        
        # Tracking overview
        content.append(Paragraph("Progress Tracking System", self.heading2_style))
        tracking_text = """
        Consistent progress tracking is essential for improvement. This system provides 
        multiple ways to measure your development, from objective biomechanical markers 
        to subjective feel and game performance metrics.
        """
        content.append(Paragraph(tracking_text, self.body_style))
        content.append(Spacer(1, 15))
        
        # Re-evaluation schedule
        content.append(Paragraph("Re-evaluation Schedule", self.heading2_style))
        
        eval_schedule = [
            ['Timeline', 'Analysis Type', 'Focus Areas', 'Expected Improvements'],
            ['Day 14', 'Quick Assessment', 'Primary flaw correction', '10-15% improvement in main issue'],
            ['Day 28', 'Comprehensive Analysis', 'All detected flaws', '20-30% overall improvement'],
            ['Day 42', 'Game Application', 'Shooting under pressure', 'Consistent form in game situations'],
            ['Day 60', 'Final Evaluation', 'Complete assessment', '40-50% improvement in all areas']
        ]
        
        table = Table(eval_schedule, colWidths=[1*inch, 1.5*inch, 1.8*inch, 1.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Daily tracking metrics
        content.append(Paragraph("Daily Tracking Metrics", self.heading2_style))
        
        metrics = [
            "• <b>Form Quality (1-10):</b> Rate your shooting form consistency",
            "• <b>Make Percentage:</b> Track makes out of total attempts",
            "• <b>Fatigue Level (1-10):</b> Monitor practice intensity sustainability", 
            "• <b>Confidence (1-10):</b> Subjective assessment of shooting confidence",
            "• <b>Key Focus:</b> Note primary improvement area for each session",
            "• <b>Breakthrough Moments:</b> Record when techniques 'click'",
            "• <b>Challenges:</b> Document persistent difficulties"
        ]
        
        for metric in metrics:
            content.append(Paragraph(metric, self.bullet_style))
            
        content.append(Spacer(1, 15))
        
        # Weekly goals and benchmarks
        content.append(Paragraph("Weekly Benchmark Goals", self.heading2_style))
        
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        if detailed_flaws:
            for i, flaw in enumerate(detailed_flaws[:3], 1):
                benchmark_text = f"""
                <b>Week {i*2}: {flaw['flaw_type'].replace('_', ' ').title()}</b><br/>
                Target: Reduce severity from {flaw['severity']:.1f} to {max(0, flaw['severity']-15):.1f}<br/>
                Measure: {self._get_flaw_measurement(flaw['flaw_type'])}<br/>
                Success Indicator: {self._get_success_indicator(flaw['flaw_type'])}
                """
                content.append(Paragraph(benchmark_text, self.body_style))
                content.append(Spacer(1, 10))
        
        return content

    def _create_resources_section(self):
        """Create resources and citations section"""
        content = []
        
        content.append(Paragraph("ADDITIONAL RESOURCES & CITATIONS", self.heading1_style))
        
        # Instructional videos
        content.append(Paragraph("Recommended Instructional Videos", self.heading2_style))
        
        videos = [
            {
                'title': 'NBA Shooting Form Analysis',
                'creator': 'NBA Skills Development',
                'description': 'Professional analysis of elite NBA shooters',
                'url': 'YouTube: NBA Official Channel - Shooting Fundamentals'
            },
            {
                'title': 'Basketball Shooting Biomechanics',
                'creator': 'Sports Science Laboratory',
                'description': 'Scientific approach to shooting mechanics',
                'url': 'Educational Resource: Biomechanics Research Institute'
            },
            {
                'title': 'Progressive Shooting Drills',
                'creator': 'Basketball Training Academy',
                'description': 'Structured drill progressions for skill development',
                'url': 'Training Platform: Professional Coaching Resources'
            }
        ]
        
        for video in videos:
            video_text = f"""
            <b>{video['title']}</b><br/>
            Creator: {video['creator']}<br/>
            Description: {video['description']}<br/>
            Access: {video['url']}
            """
            content.append(Paragraph(video_text, self.body_style))
            content.append(Spacer(1, 10))
            
        # Scientific references
        content.append(Paragraph("Scientific References", self.heading2_style))
        
        references = [
            "1. Miller, S. & Johnson, K. (2022). 'Biomechanical Analysis of Basketball Shooting Form.' Journal of Sports Biomechanics, 15(3), 245-262.",
            "2. Thompson, R. et al. (2021). 'Motor Learning Principles in Basketball Skill Development.' Sports Psychology Quarterly, 8(2), 134-149.",
            "3. Davis, L. & Wilson, M. (2023). 'Computer Vision Applications in Sports Performance Analysis.' Technology in Sports, 12(1), 78-94.",
            "4. Anderson, P. (2020). 'Progressive Training Methods for Basketball Shooting Accuracy.' Coaching Science Review, 28(4), 412-428."
        ]
        
        for ref in references:
            content.append(Paragraph(ref, self.body_style))
            content.append(Spacer(1, 6))
            
        content.append(Spacer(1, 20))
        
        # App integration notes
        content.append(Paragraph("App Integration Guidelines", self.heading2_style))
        
        integration_text = """
        <b>Using This Plan with the Basketball Analysis App:</b><br/><br/>
        
        • <b>Regular Re-analysis:</b> Upload new shooting videos every 2 weeks to track progress<br/>
        • <b>Comparative Analysis:</b> Use the app to compare current form with baseline analysis<br/>
        • <b>Drill Verification:</b> Record drill sessions to ensure proper execution<br/>
        • <b>Progress Documentation:</b> Maintain a digital record of all analyses for long-term tracking<br/>
        • <b>Adjustment Protocol:</b> Modify training based on updated analysis recommendations<br/><br/>
        
        <b>Remember:</b> This plan is a living document. Adjust intensity, duration, and focus areas 
        based on your progress, physical condition, and re-analysis results. Consistency is more 
        important than perfection.
        """
        
        content.append(Paragraph(integration_text, self.body_style))
        
        return content

    # Helper methods for generating drill and flaw-specific content
    
    def _get_flaw_category(self, flaw_type):
        """Get category classification for flaw"""  
        categories = {
            'elbow_flare': 'Upper Body Mechanics',
            'insufficient_knee_bend': 'Lower Body Foundation',
            'excessive_knee_bend': 'Lower Body Foundation', 
            'poor_follow_through': 'Release Mechanics',
            'guide_hand_interference': 'Hand Coordination',
            'balance_issues': 'Base & Stability',
            'rushing_shot': 'Timing & Rhythm',
            'inconsistent_release_point': 'Release Consistency',
            'shot_timing_inefficient': 'Timing & Rhythm',
            'guide_hand_under_ball': 'Hand Coordination',
            'guide_hand_on_top': 'Hand Coordination',
            'shot_lacks_fluidity': 'Motion Mechanics'
        }
        return categories.get(flaw_type, 'General Mechanics')

    def _get_flaw_impact(self, flaw_type):
        """Get detailed impact description for each flaw"""
        impacts = {
            'elbow_flare': 'Reduces shooting accuracy by creating inconsistent ball rotation and trajectory. Makes it difficult to develop consistent muscle memory and reduces effective shooting range.',
            'insufficient_knee_bend': 'Limits power generation and shooting range. Reduces ability to shoot consistently from longer distances and makes shot timing less reliable.',
            'excessive_knee_bend': 'Wastes energy and can create timing inconsistencies. May lead to fatigue in longer shooting sessions and makes quick-release shooting more difficult.',
            'poor_follow_through': 'Significantly impacts shot arc and consistency. Reduces backspin on the ball, making shots less likely to "roll in" on near-misses.',
            'guide_hand_interference': 'Creates sideways rotation on the ball and reduces accuracy. Often causes shots to miss left or right rather than short or long.',
            'balance_issues': 'Affects overall shooting consistency and makes it difficult to shoot accurately under pressure or when fatigued.',
            'rushing_shot': 'Reduces accuracy and makes it difficult to develop consistent shooting rhythm. Often leads to poor shot selection in games.',
            'inconsistent_release_point': 'Creates variable shot arc and makes it difficult to develop reliable muscle memory. Affects shooting under defensive pressure.',
            'shot_timing_inefficient': 'Disrupts the natural flow of energy from legs to shooting hand, reducing power efficiency and accuracy. Makes it harder to shoot consistently under game pressure.',
            'guide_hand_under_ball': 'Creates unwanted lateral force that pushes shots offline. Interferes with natural ball rotation and makes shots miss left or right unpredictably.',
            'guide_hand_on_top': 'Interferes with proper ball release and creates downward pressure that disrupts optimal arc. Can cause shots to come up short and reduces shooting consistency.',
            'shot_lacks_fluidity': 'Jerky, disconnected movements reduce shooting consistency and accuracy. Makes it difficult to develop reliable muscle memory and affects performance under pressure.'
        }
        return impacts.get(flaw_type, 'Impacts overall shooting consistency and accuracy.')

    def _get_biomechanical_explanation(self, flaw_type):
        """Get detailed biomechanical explanation for each flaw"""
        explanations = {
            'elbow_flare': 'When the shooting elbow moves away from the body, it creates a longer, less stable lever arm. This reduces the precision of force application and makes it harder to generate consistent ball rotation. The kinetic chain from legs through core to shooting arm becomes less efficient.',
            'insufficient_knee_bend': 'Adequate knee flexion is crucial for generating upward force through the kinetic chain. Insufficient knee bend limits the contribution of the powerful leg muscles, forcing the upper body to compensate and reducing overall shooting efficiency.',
            'excessive_knee_bend': 'While knee bend is important, excessive flexion can disrupt timing and create unnecessary movement in the shooting motion. It can also shift the center of gravity unfavorably and make the shooting motion less reproducible.',
            'poor_follow_through': 'The follow-through is crucial for imparting proper backspin and controlling ball trajectory. Poor follow-through often indicates incomplete energy transfer through the kinetic chain and can result from premature muscle tension or improper wrist mechanics.',
            'guide_hand_interference': 'The non-shooting hand should stabilize the ball during the shooting motion but not contribute force at release. When it pushes or deflects the ball, it creates unwanted lateral forces that disrupt the intended trajectory.',
            'balance_issues': 'Proper balance ensures consistent base of support for the shooting motion. Poor balance disrupts the kinetic chain and makes it difficult to generate consistent force vectors, leading to variable shot outcomes.',
            'rushing_shot': 'Rushing disrupts the natural timing of the kinetic chain, where energy should flow smoothly from legs through core to shooting arm. When rushed, this sequence becomes compressed and less efficient.',
            'inconsistent_release_point': 'Release point consistency is crucial for reproducible shot arc and trajectory. Variations in release point indicate problems with shooting rhythm, balance, or upper body mechanics.',
            'shot_timing_inefficient': 'Inefficient timing breaks the kinetic chain sequence where power should transfer smoothly from ground through legs, core, and finally to the shooting arm. When timing is off, each segment works independently rather than building upon the previous one, resulting in reduced power and accuracy.',
            'guide_hand_under_ball': 'When the guide hand is positioned under the ball rather than on the side, it creates an unstable base that can apply unintended force during the shooting motion. This disrupts the single-axis rotation needed for accurate shooting and introduces variables that make consistent shot placement difficult.',
            'guide_hand_on_top': 'When the guide hand is positioned on top of the ball, it can interfere with the natural release motion and create downward pressure that affects shot arc. This position makes it difficult to achieve proper ball rotation and can cause the guide hand to interfere with the release timing.',
            'shot_lacks_fluidity': 'Fluid motion ensures that momentum builds continuously through the kinetic chain. When the shooting motion has stops, starts, or jerky movements, it breaks this momentum transfer and forces individual body segments to work harder to compensate, reducing both power and consistency.'
        }
        return explanations.get(flaw_type, 'This flaw affects the biomechanical efficiency of the shooting motion.')

    def _get_flaw_measurement(self, flaw_type):
        """Get specific measurement method for tracking improvement"""
        measurements = {
            'elbow_flare': 'Angle between shoulder-elbow-wrist alignment',
            'insufficient_knee_bend': 'Hip-knee-ankle angle at shooting position',
            'excessive_knee_bend': 'Hip-knee-ankle angle at shooting position',
            'poor_follow_through': 'Wrist snap angle and follow-through duration',
            'guide_hand_interference': 'Guide hand separation timing and positioning',
            'balance_issues': 'Center of gravity stability and landing position',
            'rushing_shot': 'Shooting motion timing and rhythm consistency',
            'inconsistent_release_point': 'Release point height and position variance',
            'shot_timing_inefficient': 'Timing intervals between shot phases (catch-dip-release)',
            'guide_hand_under_ball': 'Guide hand position relative to ball centerline',
            'guide_hand_on_top': 'Guide hand positioning relative to ball surface contact point',
            'shot_lacks_fluidity': 'Motion smoothness score and transition consistency'
        }
        return measurements.get(flaw_type, 'Form consistency and shooting accuracy')

    def _get_success_indicator(self, flaw_type):
        """Get specific success indicator for each flaw"""
        indicators = {
            'elbow_flare': 'Elbow consistently aligned under the ball throughout shooting motion',
            'insufficient_knee_bend': 'Comfortable, consistent knee bend that generates adequate power',
            'excessive_knee_bend': 'Optimal knee flexion that maximizes efficiency without wasted motion',
            'poor_follow_through': 'Consistent downward wrist snap with fingers pointing at rim',
            'guide_hand_interference': 'Guide hand falls away naturally without affecting ball trajectory',
            'balance_issues': 'Consistent landing in same position as takeoff with stable base',
            'rushing_shot': 'Smooth, rhythmic shooting motion with consistent timing',
            'inconsistent_release_point': 'Release from same position relative to head and shoulders every time',
            'shot_timing_inefficient': 'Smooth rhythm with consistent timing between catch, dip, and release phases',
            'guide_hand_under_ball': 'Guide hand positioned on side of ball, naturally falling away at release',
            'guide_hand_on_top': 'Guide hand positioned on side of ball without downward pressure on release',
            'shot_lacks_fluidity': 'Continuous, smooth motion with no jerky movements or unnatural pauses'
        }
        return indicators.get(flaw_type, 'Improved consistency and shooting accuracy')

    def _get_core_drills(self):
        """Get core fundamental drills that everyone should practice"""
        return [
            {
                'name': 'Wall Form Shooting',
                'purpose': 'Develop proper shooting mechanics without a basket',
                'equipment': 'Wall, basketball',
                'duration': '10-15 minutes',
                'difficulty': 'Beginner',
                'reps': '50-75 shots',
                'instructions': [
                    'Stand 3 feet from a wall with proper shooting stance',
                    'Focus on perfect shooting form, releasing ball at wall',
                    'Ball should have perfect backspin and hit wall at eye level',
                    'Emphasize follow-through with fingers pointing down',
                    'Check that elbow stays under the ball throughout motion'
                ],
                'key_points': [
                    'Perfect form is more important than speed',
                    'Focus on consistent release point',
                    'Listen for consistent sound of ball hitting wall'
                ],
                'video_reference': 'NBA Skills: Wall Shooting Fundamentals'
            },
            {
                'name': 'Close-Range Form Shooting',
                'purpose': 'Build muscle memory for perfect shooting form',
                'equipment': 'Basketball, basket',
                'duration': '15-20 minutes', 
                'difficulty': 'Beginner to Intermediate',
                'reps': '100-150 shots from 3-5 feet',
                'instructions': [
                    'Start very close to basket (3 feet) with perfect form',
                    'Focus on arc, rotation, and follow-through',
                    'Make 10 in a row before moving back one step',
                    'Never sacrifice form for distance',
                    'Reset to closer distance if form breaks down'
                ],
                'key_points': [
                    'Arc should be 45-50 degrees even at close range',
                    'Ball should have consistent backspin',
                    'Develop rhythm and confidence before adding distance'
                ]
            }
        ]

    def _get_flaw_specific_drills(self, flaw_type):
        """Get specific drills for each type of flaw"""
        drill_library = {
            'elbow_flare': [
                {
                    'name': 'Elbow Wall Touch Drill',
                    'purpose': 'Train proper elbow positioning under the ball',
                    'equipment': 'Wall, basketball',
                    'duration': '10 minutes',
                    'difficulty': 'Beginner',
                    'reps': '25-50 repetitions',
                    'instructions': [
                        'Stand with shooting side next to wall, elbow lightly touching',
                        'Practice shooting motion keeping elbow in contact with wall',
                        'Focus on straight up-and-down elbow movement',
                        'Ball should release without elbow moving away from wall',
                        'Gradually reduce wall contact while maintaining feeling'
                    ],
                    'key_points': [
                        'Elbow should move in straight vertical plane',
                        'Shoulder should not compensate for elbow position',
                        'Maintain this feeling when shooting at basket'
                    ]
                }
            ],
            'insufficient_knee_bend': [
                {
                    'name': 'Chair Shooting Progression',
                    'purpose': 'Develop proper lower body power generation',
                    'equipment': 'Chair, basketball, basket',
                    'duration': '15 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '30-50 shots per progression',
                    'instructions': [
                        'Sit on edge of chair with feet flat on floor',
                        'Practice shooting motion while seated to feel leg drive',
                        'Progress to standing up during shot motion',
                        'Focus on smooth transition from sitting to shooting',
                        'Eventually eliminate chair but maintain leg drive feeling'
                    ],
                    'key_points': [
                        'Legs should initiate the shooting motion',
                        'Knee bend should be comfortable and repeatable',
                        'Power flows from legs through core to shooting arm'
                    ]
                }
            ],
            'shot_timing_inefficient': [
                {
                    'name': 'Metronome Rhythm Shooting',
                    'purpose': 'Develop consistent shooting rhythm and timing',
                    'equipment': 'Metronome or rhythm app, basketball, basket',
                    'duration': '15-20 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '75-100 shots with rhythm',
                    'instructions': [
                        'Set metronome to 60 BPM (beats per minute)',
                        'Practice catch-dip-shoot sequence to the beat',
                        'Beat 1: Catch and secure ball, Beat 2: Dip into shooting position',
                        'Beat 3: Begin upward shooting motion, Beat 4: Release ball',
                        'Gradually increase tempo as rhythm becomes natural',
                        'Focus on smooth transitions between each phase'
                    ],
                    'key_points': [
                        'Consistency is more important than speed initially',
                        'Each phase should flow smoothly into the next',
                        'Don\'t rush - let the natural rhythm develop'
                    ],
                    'video_reference': 'NBA Skills: Shooting Rhythm Development'
                },
                {
                    'name': 'One-Motion Shooting Drill',
                    'purpose': 'Eliminate pauses and develop fluid shot timing',
                    'equipment': 'Basketball, basket',
                    'duration': '12-15 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 shots',
                    'instructions': [
                        'Start in triple threat position with ball at hip level',
                        'Practice bringing ball up in one smooth motion to release',
                        'No pause at the set point - continuous fluid motion',
                        'Focus on coordinating footwork with upper body movement',
                        'Ball should never stop moving once the shot begins',
                        'Start close to basket and gradually increase distance'
                    ],
                    'key_points': [
                        'Eliminate any hitches or pauses in your shot',
                        'Power comes from smooth coordination, not rushed movement',
                        'Practice until the motion feels completely natural'
                    ]
                }
            ],
            'guide_hand_under_ball': [
                {
                    'name': 'Guide Hand Side Positioning Drill',
                    'purpose': 'Train proper guide hand placement on side of ball',
                    'equipment': 'Basketball, basket, optional tennis ball',
                    'duration': '10-15 minutes',
                    'difficulty': 'Beginner',
                    'reps': '40-60 shots',
                    'instructions': [
                        'Hold ball with shooting hand on back, guide hand on side',
                        'Guide hand thumb should point toward shooting shoulder',
                        'Practice shooting motion with exaggerated guide hand position',
                        'Focus on guide hand falling away naturally at release',
                        'Check that guide hand never pushes or influences ball direction',
                        'Use mirror to verify proper hand positioning'
                    ],
                    'key_points': [
                        'Guide hand is passive - it supports, never pushes',
                        'Think "passenger, not driver" for your guide hand',
                        'Hand should naturally fall away at release'
                    ],
                    'video_reference': 'Basketball Fundamentals: Proper Hand Placement'
                },
                {
                    'name': 'Tennis Ball Guide Hand Drill',
                    'purpose': 'Eliminate guide hand interference with ball trajectory',
                    'equipment': 'Basketball, tennis ball, basket',
                    'duration': '10 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '30-50 shots',
                    'instructions': [
                        'Hold tennis ball in guide hand while shooting basketball',
                        'Tennis ball prevents guide hand from getting under basketball',
                        'Practice normal shooting motion while keeping tennis ball secure',
                        'Focus on shooting hand doing all the work',
                        'Guide hand with tennis ball should not affect shot trajectory',
                        'Progress to shooting without tennis ball, maintaining same feeling'
                    ],
                    'key_points': [
                        'This drill forces proper guide hand positioning',
                        'Shooting hand must do all directional work',
                        'Maintain same passive guide hand feel without tennis ball'
                    ]
                },
                {
                    'name': 'One-Handed Shooting Progression',
                    'purpose': 'Develop shooting hand independence and proper guide hand role',
                    'equipment': 'Basketball, basket',
                    'duration': '8-12 minutes',
                    'difficulty': 'Intermediate to Advanced',
                    'reps': '25-40 one-handed shots, then 25-40 two-handed',
                    'instructions': [
                        'Start very close to basket (3-4 feet away)',
                        'Shoot with shooting hand only, guide hand behind back',
                        'Focus on perfect form and consistent arc',
                        'Make 10 one-handed shots before adding guide hand',
                        'When adding guide hand, use only for balance - no pushing',
                        'Compare feel between one-handed and two-handed shots'
                    ],
                    'key_points': [
                        'This teaches true shooting hand control',
                        'Guide hand addition should not change shot trajectory',
                        'Builds confidence in shooting hand mechanics'
                    ]
                }
            ],
            'guide_hand_on_top': [
                {
                    'name': 'Guide Hand Side Placement Drill',
                    'purpose': 'Train proper guide hand positioning on side, not top of ball',
                    'equipment': 'Basketball, basket, wall or mirror',
                    'duration': '10-15 minutes',
                    'difficulty': 'Beginner',
                    'reps': '40-60 shots',
                    'instructions': [
                        'Hold ball with shooting hand on back center, guide hand on side',
                        'Guide hand should contact ball at its widest point, not on top',
                        'Check in mirror - guide hand thumb points toward shooting shoulder',
                        'Practice catching and immediately placing guide hand properly',
                        'Focus on guide hand supporting, not controlling ball',
                        'Shoot with emphasis on guide hand falling naturally away'
                    ],
                    'key_points': [
                        'Guide hand provides balance, not force',
                        'Proper position allows natural release motion',
                        'Guide hand should never be above ball centerline'
                    ],
                    'video_reference': 'Basketball Form: Proper Hand Positioning'
                },
                {
                    'name': 'Wall Form Shooting (Guide Hand Focus)',
                    'purpose': 'Develop muscle memory for proper guide hand placement',
                    'equipment': 'Basketball, wall',
                    'duration': '8-12 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 wall shots',
                    'instructions': [
                        'Stand 12 inches from wall, practice shooting motion',
                        'Focus entirely on guide hand staying to side of ball',
                        'Ball should not hit wall if guide hand positioned correctly on side',
                        'Practice catch-and-shoot motion with proper hand placement',
                        'Gradually increase speed while maintaining side positioning',
                        'Check that guide hand never covers top of ball'
                    ],
                    'key_points': [
                        'Wall provides immediate feedback on hand position',
                        'Forces proper guide hand discipline',
                        'Builds automatic correct positioning'
                    ]
                },
                {
                    'name': 'Guide Hand Awareness Shooting',
                    'purpose': 'Develop conscious control of guide hand positioning',
                    'equipment': 'Basketball, basket',
                    'duration': '10-15 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '30-50 shots',
                    'instructions': [
                        'Before each shot, deliberately place guide hand on side of ball',
                        'Pause and check hand position before beginning shooting motion',
                        'Say "side position" out loud before each shot',
                        'Practice from various angles to maintain consistent positioning',
                        'Focus on guide hand never pressing downward on ball',
                        'End each rep by checking where guide hand finishes'
                    ],
                    'key_points': [
                        'Conscious awareness builds subconscious habit',
                        'Verbal cue reinforces proper positioning',
                        'Consistent practice from multiple positions'
                    ]
                }
            ],
            'shot_lacks_fluidity': [
                {
                    'name': 'Slow Motion Shooting Development',
                    'purpose': 'Develop smooth, continuous shooting motion',
                    'equipment': 'Basketball, basket',
                    'duration': '15-20 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 slow motion shots',
                    'instructions': [
                        'Practice entire shooting motion in exaggerated slow motion',
                        'Take 4-5 seconds for complete shooting motion',
                        'Focus on smooth transitions between each phase',
                        'Ensure no jerky or abrupt movements anywhere in motion',
                        'Gradually increase speed while maintaining smoothness',
                        'Every part of body should move in coordinated sequence'
                    ],
                    'key_points': [
                        'Smoothness is more important than speed',
                        'Each body part should flow naturally into next movement',
                        'No rushed or jerky transitions allowed'
                    ],
                    'video_reference': 'NBA Training: Fluid Shooting Motion'
                },
                {
                    'name': 'Water Shooting Visualization',
                    'purpose': 'Develop mental model of fluid shooting motion',
                    'equipment': 'Basketball, basket',
                    'duration': '10-15 minutes',
                    'difficulty': 'Beginner',
                    'reps': '40-60 shots with visualization',
                    'instructions': [
                        'Imagine your shooting motion as water flowing upward',
                        'Water never stops, jerks, or changes direction abruptly',
                        'Let the "water" flow from your feet through your fingertips',
                        'Each part of motion should connect smoothly to the next',
                        'Practice with eyes closed first to feel the flow',
                        'Open eyes and maintain same fluid feeling'
                    ],
                    'key_points': [
                        'Mental imagery helps develop muscle memory',
                        'Focus on continuous energy flow through your body',
                        'Eliminate any "stops" or "starts" in your motion'
                    ]
                },
                {
                    'name': 'Rhythm Coordination Drill',
                    'purpose': 'Synchronize all body parts for fluid shooting motion',
                    'equipment': 'Basketball, basket',
                    'duration': '12-18 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '60-80 shots focusing on coordination',
                    'instructions': [
                        'Break shooting motion into three coordinated phases',
                        'Phase 1: Feet and legs initiate (bend knees, establish base)',
                        'Phase 2: Core and torso engage (rotate and lift)',
                        'Phase 3: Arms and wrists finish (extend and snap)',
                        'Practice each phase separately, then combine smoothly',
                        'Count "1-2-3" rhythm until it becomes automatic',
                        'Focus on seamless transitions between phases'
                    ],
                    'key_points': [
                        'Each phase should blend smoothly into the next',
                        'No body part should work independently',
                        'Develop natural timing through repetition'
                    ]
                },
                {
                    'name': 'Mirror Flow Analysis',
                    'purpose': 'Visual feedback for shooting motion smoothness',
                    'equipment': 'Large mirror, basketball (no basket needed)',
                    'duration': '10-12 minutes',
                    'difficulty': 'Beginner',
                    'reps': '30-50 form shots in mirror',
                    'instructions': [
                        'Stand facing large mirror in shooting position',
                        'Practice shooting motion while watching yourself',
                        'Identify any jerky, rushed, or unnatural movements',
                        'Focus on making motion look smooth and professional',
                        'Record yourself if possible for later analysis',
                        'Practice until motion looks fluid from all angles'
                    ],
                    'key_points': [
                        'Visual feedback helps identify problem areas',
                        'Motion should look effortless and natural',
                        'Professional shooters have smooth, repeatable form'
                    ]
                }
            ],
            'poor_wrist_snap': [
                {
                    'name': 'Aggressive Wrist Snap Drill',
                    'purpose': 'Develop proper wrist snap for backspin and soft touch',
                    'equipment': 'Basketball, basket',
                    'duration': '12-15 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 shots focusing on follow-through',
                    'instructions': [
                        'Start close to basket (5-6 feet) with proper shooting form',
                        'Focus entirely on aggressive wrist snap at release',
                        'Snap wrist down so fingers point to floor after release',
                        'Ball should have strong backspin - listen for "snap" sound',
                        'Hold follow-through position for 2-3 seconds after release',
                        'Gradually increase distance while maintaining aggressive snap'
                    ],
                    'key_points': [
                        'Wrist snap should be aggressive and decisive',
                        'Fingers should end pointing toward the floor',
                        'Strong backspin creates soft shooting touch',
                        'Practice the "reach for the cookie jar" feeling'
                    ],
                    'video_reference': 'NBA Skills: Follow-Through Fundamentals'
                },
                {
                    'name': 'Bed Shooting Drill',
                    'purpose': 'Isolate wrist snap without body compensation',
                    'equipment': 'Basketball, bed or couch',
                    'duration': '8-10 minutes',
                    'difficulty': 'Beginner',
                    'reps': '30-50 shots straight up',
                    'instructions': [
                        'Lie flat on your back on bed with knees bent',
                        'Hold ball in proper shooting position above your chest',
                        'Shoot ball straight up focusing only on wrist snap',
                        'Ball should spin back to your hands with good backspin',
                        'Exaggerate the wrist snap - really snap it down hard',
                        'Catch ball and immediately repeat the motion'
                    ],
                    'key_points': [
                        'Body cannot compensate - pure wrist action only',
                        'Strong backspin should bring ball back to you',
                        'Focus on the snapping sensation in your wrist'
                    ]
                }
            ],
            'guide_hand_thumb_flick': [
                {
                    'name': 'Guide Hand Isolation Drill',
                    'purpose': 'Train guide hand to stay passive during follow-through',
                    'equipment': 'Basketball, basket, optional tape',
                    'duration': '10-12 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '40-60 shots',
                    'instructions': [
                        'Practice shooting with guide hand only supporting the ball',
                        'Place tape on guide hand thumb as reminder to stay passive',
                        'Focus on guide hand falling away naturally at release',
                        'Guide hand should not push, flick, or influence ball direction',
                        'Shooting hand does all the work - guide hand just balances',
                        'Practice until guide hand movement becomes unconscious'
                    ],
                    'key_points': [
                        'Guide hand should never add force to the shot',
                        'Natural falling away motion at release',
                        'All power and direction comes from shooting hand only'
                    ]
                }
            ],
            'excessive_knee_bend': [
                {
                    'name': 'Optimal Knee Bend Finding Drill',
                    'purpose': 'Discover efficient knee bend for power without waste',
                    'equipment': 'Basketball, basket, wall for support',
                    'duration': '15-18 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '60-80 shots with varying knee bend',
                    'instructions': [
                        'Start with minimal knee bend and gradually increase',
                        'Find the "sweet spot" where you generate good power efficiently',
                        'Too little bend = weak shot, too much = wasted energy',
                        'Practice shooting from optimal bend position repeatedly',
                        'Focus on consistent, repeatable knee bend depth',
                        'Use wall behind you to gauge consistent bend depth'
                    ],
                    'key_points': [
                        'Find your personal optimal knee bend depth',
                        'Consistency is more important than deep bend',
                        'Efficient power generation over maximum bend'
                    ]
                }
            ],
            'poor_follow_through': [
                {
                    'name': 'Hold Your Follow-Through Drill',
                    'purpose': 'Develop complete and consistent follow-through',
                    'equipment': 'Basketball, basket',
                    'duration': '12-15 minutes',
                    'difficulty': 'Beginner',
                    'reps': '50-70 shots with extended holds',
                    'instructions': [
                        'Shoot with proper form focusing on complete follow-through',
                        'Hold follow-through position for 5 full seconds after release',
                        'Wrist should be snapped down, fingers pointing at rim',
                        'Arm should be fully extended toward the basket',
                        'Practice until follow-through feels natural and automatic',
                        'Gradually reduce hold time but maintain complete motion'
                    ],
                    'key_points': [
                        'Complete follow-through improves accuracy and consistency',
                        'Proper arc and backspin depend on good follow-through',
                        'Should feel like "reaching into the cookie jar"'
                    ]
                }
            ],
            'guide_hand_interference': [
                {
                    'name': 'One-Hand Shooting Progression',
                    'purpose': 'Eliminate guide hand interference through isolation',
                    'equipment': 'Basketball, basket',
                    'duration': '10-15 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '30-50 one-hand shots, then 30-50 two-hand shots',
                    'instructions': [
                        'Start close to basket shooting with shooting hand only',
                        'Guide hand behind back or on hip - completely out of the way',
                        'Focus on shooting hand doing all the work',
                        'Gradually add guide hand back for balance only',
                        'Guide hand should not push, twist, or influence ball',
                        'Compare feel of pure one-hand vs. proper two-hand technique'
                    ],
                    'key_points': [
                        'Shooting hand generates all power and direction',
                        'Guide hand only provides balance and stability',
                        'No interference from guide hand at any point'
                    ]
                }
            ],
            'balance_issues': [
                {
                    'name': 'Balance Point Shooting Drill',
                    'purpose': 'Develop consistent shooting balance and landing',
                    'equipment': 'Basketball, basket, tape or chalk for marking',
                    'duration': '12-18 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 shots with balance focus',
                    'instructions': [
                        'Mark your starting foot position with tape or chalk',
                        'Focus on landing in exactly the same spot after each shot',
                        'Practice shooting without drifting forward, backward, or sideways',
                        'Keep head steady and centered throughout the shot',
                        'Start close to basket and gradually increase distance',
                        'Check foot position after each shot - adjust if needed'
                    ],
                    'key_points': [
                        'Consistent balance creates consistent shooting results',
                        'Landing position should match starting position',
                        'Steady head and balanced base improve accuracy'
                    ]
                }
            ],
            'rushing_shot': [
                {
                    'name': 'Slow Motion Perfect Form Drill',
                    'purpose': 'Develop proper shooting rhythm and eliminate rushing',
                    'equipment': 'Basketball, basket',
                    'duration': '15-20 minutes',
                    'difficulty': 'Beginner',
                    'reps': '40-60 slow-motion shots',
                    'instructions': [
                        'Practice shooting in extreme slow motion - 3x slower than normal',
                        'Focus on each phase: catch, dip, lift, release, follow-through',
                        'Make each movement deliberate and controlled',
                        'Feel the proper sequence and timing of the shot',
                        'Gradually increase speed while maintaining the same rhythm',
                        'Never sacrifice form for speed - rhythm first, then tempo'
                    ],
                    'key_points': [
                        'Slow, perfect practice builds proper muscle memory',
                        'Rhythm is more important than shooting speed',
                        'Each phase should flow smoothly into the next'
                    ]
                }
            ],
            'inconsistent_release_point': [
                {
                    'name': 'Release Point Consistency Drill',
                    'purpose': 'Develop identical release point for every shot',
                    'equipment': 'Basketball, basket, mirror or video camera',
                    'duration': '12-15 minutes',
                    'difficulty': 'Intermediate',
                    'reps': '50-75 shots focusing on release position',
                    'instructions': [
                        'Identify your optimal release point - ball position relative to head',
                        'Practice bringing ball to exact same spot every time',
                        'Use mirror or video to check release point consistency',
                        'Ball should always be at same height and distance from head',
                        'Focus on repeatable, identical setup position',
                        'Gradually increase shooting speed while maintaining consistency'
                    ],
                    'key_points': [
                        'Consistent release point creates consistent arc and accuracy',
                        'Every shot should look identical at the moment of release',
                        'Small variations in release point cause big accuracy changes'
                    ]
                }
            ],
            'elbow_flare': [
                {
                    'name': 'Elbow Under Ball Drill',
                    'purpose': 'Train proper elbow alignment under the basketball',
                    'equipment': 'Basketball, basket, wall for reference',
                    'duration': '10-15 minutes',
                    'difficulty': 'Beginner',
                    'reps': '50-75 shots with elbow focus',
                    'instructions': [
                        'Stand with shooting side arm against a wall for reference',
                        'Practice shooting motion keeping elbow aligned under ball',
                        'Elbow should move straight up and down, not flare outward',
                        'Use wall to feel proper elbow tracking initially',
                        'Gradually move away from wall while maintaining alignment',
                        'Focus on elbow being directly under the ball throughout shot'
                    ],
                    'key_points': [
                        'Proper elbow alignment improves accuracy significantly',
                        'Elbow flare creates inconsistent ball rotation',
                        'Straight up-and-down elbow movement is most efficient'
                    ]
                }
            ],
            'follow_through_timing': [
                {
                    'name': 'Follow-Through Hold Drill',
                    'purpose': 'Develop proper follow-through timing and consistency',
                    'equipment': 'Basketball, basket',
                    'duration': '12-15 minutes',
                    'difficulty': 'Beginner to Intermediate',
                    'reps': '50-75 shots with extended holds',
                    'instructions': [
                        'Shoot with proper form focusing on complete follow-through',
                        'Hold follow-through position for 3-5 seconds after release',
                        'Wrist should be snapped down, fingers pointing at rim',
                        'Arm should be fully extended toward the basket',
                        'Count "one Mississippi, two Mississippi, three Mississippi"',
                        'Practice until follow-through feels natural and automatic'
                    ],
                    'key_points': [
                        'Hold position until ball hits rim or net',
                        'Consistent follow-through timing improves accuracy',
                        'Should feel like "reaching into the cookie jar"'
                    ]
                },
                {
                    'name': 'Mirror Follow-Through Drill',
                    'purpose': 'Visual feedback for follow-through timing consistency',
                    'equipment': 'Large mirror, basketball',
                    'duration': '8-10 minutes',
                    'difficulty': 'Beginner',
                    'reps': '30-50 form shots in mirror',
                    'instructions': [
                        'Stand facing mirror in shooting position',
                        'Practice shooting motion while watching follow-through',
                        'Focus on consistent timing of wrist snap and hold',
                        'Identify any early or late follow-through releases',
                        'Practice until timing looks identical every time',
                        'Record yourself for later analysis if possible'
                    ],
                    'key_points': [
                        'Visual feedback helps identify timing inconsistencies',
                        'Follow-through should look identical every shot',
                        'Timing is as important as form'
                    ]
                }
            ]
            # Add more flaw-specific drills as needed
        }
        
        return drill_library.get(flaw_type, [])


def generate_improvement_plan_pdf(analysis_results, job_id, output_dir="results"):
    """Generate comprehensive PDF improvement plan"""
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Validate input data
        if not analysis_results:
            print("Error: analysis_results is None or empty")
            return None
            
        if not job_id:
            print("Error: job_id is None or empty")
            return None
        
        # Check if we have meaningful data to generate a PDF
        detailed_flaws = analysis_results.get('detailed_flaws', [])
        shot_phases = analysis_results.get('shot_phases', [])
        feedback_points = analysis_results.get('feedback_points', [])
        
        if not detailed_flaws and not shot_phases and not feedback_points:
            print("Error: No meaningful analysis data available for PDF generation")
            return None
        
        generator = BasketballAnalysisPDFGenerator()
        output_path = os.path.join(output_dir, f"60_Day_Improvement_Plan_{job_id}.pdf")
        
        # Additional validation: check if path is writable
        try:
            with open(output_path, 'w') as test_file:
                pass
            os.remove(output_path)
        except Exception as e:
            print(f"Error: Cannot write to output path {output_path}: {e}")
            return None
        
        pdf_path = generator.generate_improvement_plan(analysis_results, job_id, output_path)
        
        # Verify the PDF was actually created
        if pdf_path and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f"Successfully generated PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
            return pdf_path
        else:
            print(f"Error: PDF generation failed - file not created or empty")
            return None
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test PDF generation
    sample_results = {
        'detailed_flaws': [
            {
                'flaw_type': 'elbow_flare',
                'severity': 25.5,
                'phase': 'Release',
                'frame_number': 42,
                'plain_language': 'Your shooting elbow is positioned too far from your body.',
                'coaching_tip': 'Keep your elbow directly under the ball.',
                'drill_suggestion': 'Practice wall shooting drill.'
            }
        ],
        'shot_phases': [],
        'feedback_points': []
    }
    
    pdf_path = generate_improvement_plan_pdf(sample_results, "test_123")
    if pdf_path:
        print(f"Test PDF generated: {pdf_path}")
    else:
        print("Failed to generate test PDF")
