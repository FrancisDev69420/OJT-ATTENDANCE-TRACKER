"""
Example Usage Script - Attendance Analysis System

Demonstrates how to use the AttendanceAnalyzer class directly
and provides practical examples for common use cases.

Run this script to see the system in action:
    python example_usage.py
"""

from attendance_analysis import AttendanceAnalyzer
import json
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


def example_1_get_all_students_risk():
    """Example 1: Get risk classification for all students"""
    print_section("Example 1: Risk Classification for All Students")
    
    analyzer = AttendanceAnalyzer()
    risk_summary = analyzer.get_risk_summary()
    
    print(f"\nTotal Students: {risk_summary['total_students']}")
    print(f"\nRisk Distribution:")
    for risk_level, count in risk_summary['risk_distribution'].items():
        percentage = (count / risk_summary['total_students'] * 100) if risk_summary['total_students'] > 0 else 0
        print(f"  {risk_level.upper()}: {count} students ({percentage:.1f}%)")
    
    if risk_summary['critical_students']:
        print(f"\n🔴 CRITICAL STUDENTS ({len(risk_summary['critical_students'])}):")
        for student in risk_summary['critical_students']:
            print(f"  - {student['name']} ({student['attendance_rate']:.1f}% attendance)")


def example_2_detailed_student_analysis(student_id=None):
    """Example 2: Get detailed analysis for a specific student"""
    print_section("Example 2: Detailed Student Analysis")
    
    analyzer = AttendanceAnalyzer()
    
    # If no student_id provided, get the first student
    if student_id is None:
        analyzer.load_data()
        if analyzer.students_df.empty:
            print("⚠️ No students found in database")
            return
        student_id = analyzer.students_df['id'].iloc[0]
    
    print(f"\nAnalyzing student: {student_id}\n")
    
    analysis = analyzer.get_student_analysis(student_id)
    
    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return
    
    # Print summary
    print(f"Name: {analysis['student_name']}")
    print(f"Risk Level: {analysis['risk_classification'].upper()}")
    
    # Attendance Summary
    summary = analysis['summary']
    print(f"\n📊 Attendance Summary:")
    print(f"  Total Days: {summary['total_days']}")
    print(f"  Present: {summary['present_count']}")
    print(f"  Late: {summary['late_count']}")
    print(f"  Absent: {summary['absent_count']}")
    print(f"  Half-days: {summary['half_day_count']}")
    print(f"  Holidays: {summary['holiday_count']}")
    print(f"  Attendance Rate: {summary['attendance_rate']:.1f}%")
    print(f"  Pattern: {summary['pattern']}")
    
    # Hours tracking
    hours = analysis['hours']
    print(f"\n⏱️ Hours Tracking:")
    print(f"  Required: {hours['required_hours']} hours")
    print(f"  Rendered: {hours['hours_rendered']:.1f} hours")
    print(f"  Remaining: {hours['remaining_hours']:.1f} hours")
    print(f"  Completion: {hours['hours_completion_percentage']:.1f}%")
    
    # Trend analysis
    trend = analysis['trend']
    print(f"\n📈 Trend Analysis:")
    if trend['trend'] != 'insufficient_data':
        print(f"  Direction: {trend['trend'].upper()}")
        print(f"  First Half Rate: {trend['first_half_rate']:.1f}%")
        print(f"  Second Half Rate: {trend['second_half_rate']:.1f}%")
        print(f"  Change: {trend['change_percentage']:+.1f}%")
    else:
        print(f"  Not enough data for trend analysis")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"  {i}. {rec}")


def example_3_identify_struggling_students():
    """Example 3: Identify students who need intervention"""
    print_section("Example 3: Identify Struggling Students")
    
    analyzer = AttendanceAnalyzer()
    all_analysis = analyzer.get_all_students_analysis()
    
    # Filter students by risk level
    warning_students = [s for s in all_analysis if s.get('risk_classification') == 'warning' and 'error' not in s]
    critical_students = [s for s in all_analysis if s.get('risk_classification') == 'critical' and 'error' not in s]
    
    print(f"\n⚠️  WARNING LEVEL ({len(warning_students)} students):")
    if warning_students:
        for student in warning_students:
            print(f"  - {student['student_name']}: {student['summary']['attendance_rate']:.1f}% attendance, "
                  f"{student['hours']['remaining_hours']:.1f} hours remaining")
    else:
        print("  No students in warning level")
    
    print(f"\n🔴 CRITICAL LEVEL ({len(critical_students)} students):")
    if critical_students:
        for student in critical_students:
            print(f"  - {student['student_name']}: {student['summary']['attendance_rate']:.1f}% attendance, "
                  f"{student['hours']['remaining_hours']:.1f} hours remaining")
    else:
        print("  No students in critical level")


def example_4_attendance_summary_only():
    """Example 4: Get quick attendance summary (minimal data)"""
    print_section("Example 4: Quick Attendance Summary")
    
    analyzer = AttendanceAnalyzer()
    analyzer.load_data()
    
    if analyzer.students_df.empty:
        print("⚠️ No students found in database")
        return
    
    # Get first 3 students
    student_ids = analyzer.students_df['id'].iloc[:3]
    
    print(f"\nQuick Summary for First {min(3, len(student_ids))} Students:\n")
    
    for student_id in student_ids:
        summary = analyzer.get_student_attendance_summary(student_id)
        student_name = analyzer.students_df[analyzer.students_df['id'] == student_id]['name'].values[0]
        
        print(f"📋 {student_name}")
        print(f"   Attendance Rate: {summary['attendance_rate']:.1f}%")
        print(f"   Present: {summary['present_count']} | Late: {summary['late_count']} | Absent: {summary['absent_count']}")
        print(f"   Pattern: {summary['pattern']}\n")


def example_5_overall_statistics():
    """Example 5: Get overall system statistics"""
    print_section("Example 5: Overall System Statistics")
    
    analyzer = AttendanceAnalyzer()
    analyzer.load_data()
    
    students_df = analyzer.students_df
    attendances_df = analyzer.attendances_df
    
    print(f"\n📊 System Overview:")
    print(f"  Total Students: {len(students_df)}")
    print(f"  Total Attendance Records: {len(attendances_df)}")
    print(f"  Average Hours Rendered: {attendances_df['hours_rendered'].mean():.2f} hours")
    print(f"  Total Hours Rendered: {attendances_df['hours_rendered'].sum():.2f} hours")
    
    print(f"\n📈 Status Breakdown:")
    status_counts = attendances_df['status'].value_counts()
    for status, count in status_counts.items():
        percentage = (count / len(attendances_df) * 100)
        print(f"  {status.upper()}: {count} records ({percentage:.1f}%)")


def example_6_compare_students():
    """Example 6: Compare attendance between students"""
    print_section("Example 6: Compare Student Performance")
    
    analyzer = AttendanceAnalyzer()
    all_analysis = analyzer.get_all_students_analysis()
    
    if len(all_analysis) < 2:
        print("⚠️ Need at least 2 students to compare")
        return
    
    # Get top and bottom performers
    valid_students = [s for s in all_analysis if 'error' not in s]
    
    if not valid_students:
        print("⚠️ No valid student data to compare")
        return
    
    sorted_by_attendance = sorted(valid_students, key=lambda x: x['summary']['attendance_rate'], reverse=True)
    
    print(f"\n⭐ TOP 3 PERFORMERS (by attendance rate):")
    for i, student in enumerate(sorted_by_attendance[:3], 1):
        print(f"  {i}. {student['student_name']}: {student['summary']['attendance_rate']:.1f}% "
              f"({student['risk_classification'].upper()})")
    
    print(f"\n⚠️ BOTTOM 3 PERFORMERS (by attendance rate):")
    for i, student in enumerate(sorted_by_attendance[-3:], 1):
        print(f"  {i}. {student['student_name']}: {student['summary']['attendance_rate']:.1f}% "
              f"({student['risk_classification'].upper()})")


def example_7_json_export():
    """Example 7: Export student analysis as JSON"""
    print_section("Example 7: Export Student Analysis (JSON)")
    
    analyzer = AttendanceAnalyzer()
    analyzer.load_data()
    
    if analyzer.students_df.empty:
        print("⚠️ No students found in database")
        return
    
    student_id = analyzer.students_df['id'].iloc[0]
    analysis = analyzer.get_student_analysis(student_id)
    
    print(f"\nJSON Export for {analysis['student_name']}:")
    print_json(analysis)


def main():
    """Run all examples"""
    print("\n" + "🎓" * 40)
    print("  ATTENDANCE ANALYSIS SYSTEM - USAGE EXAMPLES")
    print("🎓" * 40)
    
    try:
        # Run examples
        example_1_get_all_students_risk()
        example_2_detailed_student_analysis()
        example_3_identify_struggling_students()
        example_4_attendance_summary_only()
        example_5_overall_statistics()
        example_6_compare_students()
        example_7_json_export()
        
        print("\n" + "=" * 80)
        print(" ✅ All examples completed successfully!")
        print("=" * 80)
        
        print("\n📌 Next Steps:")
        print("  1. Run the FastAPI server: python attendance_api.py")
        print("  2. Access API docs: http://localhost:8000/docs")
        print("  3. Integrate with your Laravel frontend")
        print("  4. See ATTENDANCE_ANALYSIS_GUIDE.md for complete documentation\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nTroubleshooting:")
        print("  - Ensure MySQL is running")
        print("  - Verify database credentials in attendance_analysis.py")
        print("  - Check that students and attendance records exist in the database")
        print("  - Review error message above for specific issues\n")


if __name__ == "__main__":
    main()
