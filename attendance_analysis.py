import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

# Database connection
def get_db_engine():
    """Create and return database engine for MySQL connection"""
    return create_engine('mysql+pymysql://root:Reyes123!@localhost/ojt_attendance_tracker')


class AttendanceAnalyzer:
    """
    AI-based attendance pattern analyzer using pandas.
    
    Analyzes student attendance patterns and provides:
    - Attendance statistics (present, late, absent counts)
    - Attendance rate percentage
    - Risk classification (excellent, good, warning, critical)
    - Trend analysis
    """
    
    def __init__(self):
        """Initialize the analyzer with database connection"""
        self.engine = get_db_engine()
        self.students_df = None
        self.attendances_df = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load students and attendance data from database"""
        self.students_df = pd.read_sql('SELECT * FROM students', self.engine)
        self.attendances_df = pd.read_sql('SELECT * FROM attendances', self.engine)
        return self.students_df, self.attendances_df
    
    def get_student_attendance_summary(self, student_id: str) -> Dict:
        """
        Get attendance summary for a specific student.
        
        Args:
            student_id: UUID of the student
            
        Returns:
            Dictionary containing attendance counts and statistics
        """
        # Load fresh data
        self.load_data()
        
        # Filter attendance for specific student
        student_attendance = self.attendances_df[
            self.attendances_df['student_id'] == student_id
        ]
        
        if student_attendance.empty:
            return {
                'student_id': student_id,
                'total_days': 0,
                'present_count': 0,
                'late_count': 0,
                'absent_count': 0,
                'half_day_count': 0,
                'holiday_count': 0,
                'attendance_rate': 0.0,
                'pattern': None
            }
        
        # Count statuses
        status_counts = student_attendance['status'].value_counts().to_dict()
        total_days = len(student_attendance)
        
        present = status_counts.get('present', 0)
        late = status_counts.get('late', 0)
        absent = status_counts.get('absent', 0)
        half_day = status_counts.get('half_day', 0)
        holiday = status_counts.get('holiday', 0)
        
        # Calculate attendance rate (present and late count as attended)
        attended_days = present + late + half_day
        attendance_rate = (attended_days / total_days * 100) if total_days > 0 else 0
        
        return {
            'student_id': student_id,
            'total_days': total_days,
            'present_count': present,
            'late_count': late,
            'absent_count': absent,
            'half_day_count': half_day,
            'holiday_count': holiday,
            'hours_rendered': float(student_attendance['hours_rendered'].sum()),
            'attendance_rate': round(attendance_rate, 2),
            'pattern': self._identify_pattern(present, late, absent, total_days)
        }
    
    def get_student_analysis(self, student_id: str) -> Dict:
        """
        Get complete analysis for a student including risk classification.
        
        Args:
            student_id: UUID of the student
            
        Returns:
            Comprehensive analysis dictionary
        """
        # Load student data
        self.load_data()
        
        student = self.students_df[self.students_df['id'] == student_id]
        if student.empty:
            return {'error': 'Student not found'}
        
        summary = self.get_student_attendance_summary(student_id)
        
        # Check if student has minimum 10 days of attendance records
        if summary['total_days'] < 10:
            return {'error': f'Insufficient data: Student has {summary["total_days"]} days of attendance records. Minimum 10 days required for analysis.'}
        
        # Get required hours
        required_hours = float(student['required_hours'].values[0])
        hours_rendered = summary['hours_rendered']
        remaining_hours = max(0, required_hours - hours_rendered)
        
        # Classify risk
        risk_classification = self._classify_risk(
            summary['attendance_rate'],
            summary['absent_count'],
            summary['total_days'],
            remaining_hours,
            required_hours
        )
        
        # Get trend
        trend = self._analyze_trend(student_id)
        
        return {
            'student_id': student_id,
            'student_name': student['name'].values[0],
            'summary': summary,
            'hours': {
                'required_hours': required_hours,
                'hours_rendered': hours_rendered,
                'remaining_hours': remaining_hours,
                'hours_completion_percentage': round((hours_rendered / required_hours * 100), 2) if required_hours > 0 else 0
            },
            'risk_classification': risk_classification,
            'trend': trend,
            'recommendations': self._get_recommendations(risk_classification, summary, remaining_hours)
        }
    
    def _identify_pattern(self, present: int, late: int, absent: int, total: int) -> str:
        """
        Identify attendance pattern based on counts.
        
        Pattern types:
        - consistent: 90%+ attendance rate
        - irregular: 70-89% attendance rate
        - concerning: 50-69% attendance rate
        - critical: <50% attendance rate
        """
        if total == 0:
            return 'no_data'
        
        attended = present + late
        rate = (attended / total) * 100
        
        if rate >= 90:
            return 'consistent'
        elif rate >= 70:
            return 'irregular'
        elif rate >= 50:
            return 'concerning'
        else:
            return 'critical'
    
    def _classify_risk(self, attendance_rate: float, absent_count: int, 
                       total_days: int, remaining_hours: float, required_hours: float) -> str:
        """
        Classify student risk level based on multiple factors.
        
        Factors considered:
        - Attendance rate (40% weight)
        - Absence count (30% weight)
        - Hours completion (30% weight)
        """
        if total_days == 0:
            return 'insufficient_data'
        
        # Calculate weighted score (0-100)
        attendance_score = attendance_rate * 0.4
        
        absence_score = (1 - min(absent_count / max(total_days / 3, 1), 1)) * 100 * 0.3
        
        hours_score = (1 - (remaining_hours / max(required_hours, 1))) * 100 * 0.3
        
        total_score = attendance_score + absence_score + hours_score
        
        # Classify based on score
        if total_score >= 80:
            return 'excellent'
        elif total_score >= 60:
            return 'good'
        elif total_score >= 40:
            return 'warning'
        else:
            return 'critical'
    
    def _analyze_trend(self, student_id: str) -> Dict:
        """
        Analyze attendance trend over time (improving, stable, declining).
        
        Compares recent attendance rate with overall attendance rate.
        """
        student_attendance = self.attendances_df[
            self.attendances_df['student_id'] == student_id
        ].sort_values('date')
        
        if len(student_attendance) < 4:
            return {'trend': 'insufficient_data', 'direction': None}
        
        # Split into first half and second half
        mid_point = len(student_attendance) // 2
        first_half = student_attendance.iloc[:mid_point]
        second_half = student_attendance.iloc[mid_point:]
        
        # Calculate attendance rates
        first_rate = self._calculate_attendance_rate(first_half)
        second_rate = self._calculate_attendance_rate(second_half)
        
        # Determine trend direction
        difference = second_rate - first_rate
        
        if abs(difference) < 5:
            direction = 'stable'
        elif difference > 5:
            direction = 'improving'
        else:
            direction = 'declining'
        
        return {
            'trend': direction,
            'first_half_rate': round(first_rate, 2),
            'second_half_rate': round(second_rate, 2),
            'change_percentage': round(difference, 2)
        }
    
    def _calculate_attendance_rate(self, attendance_df: pd.DataFrame) -> float:
        """Calculate attendance rate for a dataframe"""
        if attendance_df.empty:
            return 0
        attended = len(attendance_df[attendance_df['status'].isin(['present', 'late'])])
        return (attended / len(attendance_df)) * 100
    
    def _get_recommendations(self, risk_classification: str, summary: Dict, 
                            remaining_hours: float) -> List[str]:
        """
        Generate recommendations based on risk classification and attendance pattern.
        """
        recommendations = []
        
        if risk_classification == 'critical':
            recommendations.append('Critical: Immediate intervention required. Student attendance is severely below acceptable levels.')
            if summary['absent_count'] > summary['total_days'] * 0.3:
                recommendations.append('Student has excessive absences. Consider meeting to discuss barriers to attendance.')
            if remaining_hours > 0:
                recommendations.append(f'Student needs to render {remaining_hours} more hours to meet requirements.')
        
        elif risk_classification == 'warning':
            recommendations.append('Warning: Student attendance is below acceptable levels. Monitor closely.')
            if summary['late_count'] > summary['total_days'] * 0.2:
                recommendations.append('Student has frequent late arrivals. Discuss punctuality expectations.')
            if remaining_hours > 0:
                recommendations.append(f'Student should prioritize rendering remaining {remaining_hours} hours.')
        
        elif risk_classification == 'good':
            recommendations.append('Good: Student attendance is acceptable. Maintain current level.')
            if summary['pattern'] == 'irregular':
                recommendations.append('Student shows some inconsistency. Encourage maintaining consistent attendance.')
        
        elif risk_classification == 'excellent':
            recommendations.append('Excellent: Student demonstrates outstanding attendance and commitment.')
            recommendations.append('Student is on track to complete all requirements.')
        
        return recommendations
    
    def get_all_students_analysis(self) -> List[Dict]:
        """Get analysis for all students"""
        self.load_data()
        
        results = []
        for student_id in self.students_df['id'].unique():
            analysis = self.get_student_analysis(student_id)
            results.append(analysis)
        
        return results
    
    def get_risk_summary(self) -> Dict:
        """Get summary of all students by risk classification"""
        all_analysis = self.get_all_students_analysis()
        
        risk_counts = {
            'excellent': 0,
            'good': 0,
            'warning': 0,
            'critical': 0,
            'insufficient_data': 0
        }
        
        for student_data in all_analysis:
            if 'error' not in student_data:
                risk = student_data['risk_classification']
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        return {
            'total_students': len([s for s in all_analysis if 'error' not in s]),
            'risk_distribution': risk_counts,
            'critical_students': [
                {
                    'name': s['student_name'],
                    'student_id': s['student_id'],
                    'attendance_rate': s['summary']['attendance_rate']
                }
                for s in all_analysis if s.get('risk_classification') == 'critical' and 'error' not in s
            ]
        }


# Initialize analyzer for direct usage
analyzer = AttendanceAnalyzer()

