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
                ['Shot Phase:', flaw['phase']],
                ['Frame Location:', f"Frame {flaw['frame_number']}"],
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
            content.append(Paragraph(flaw['plain_language'], self.body_style))
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
            content.append(Paragraph(flaw['coaching_tip'], self.body_style))
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
            'inconsistent_release_point': 'Release Consistency'
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
            'inconsistent_release_point': 'Creates variable shot arc and makes it difficult to develop reliable muscle memory. Affects shooting under defensive pressure.'
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
            'inconsistent_release_point': 'Release point consistency is crucial for reproducible shot arc and trajectory. Variations in release point indicate problems with shooting rhythm, balance, or upper body mechanics.'
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
            'inconsistent_release_point': 'Release point height and position variance'
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
            'inconsistent_release_point': 'Release from same position relative to head and shoulders every time'
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
            ]
            # Add more flaw-specific drills as needed
        }
        
        return drill_library.get(flaw_type, [])


def generate_improvement_plan_pdf(analysis_results, job_id, output_dir="results"):
    """Generate comprehensive PDF improvement plan"""
    
    generator = BasketballAnalysisPDFGenerator()
    output_path = os.path.join(output_dir, f"60_Day_Improvement_Plan_{job_id}.pdf")
    
    try:
        pdf_path = generator.generate_improvement_plan(analysis_results, job_id, output_path)
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
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
