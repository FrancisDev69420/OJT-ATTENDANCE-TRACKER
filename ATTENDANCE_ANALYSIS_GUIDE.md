# Attendance Analysis System Guide

## Overview

This system provides **AI-powered attendance pattern analysis** for the OJT Attendance Tracker using pandas and FastAPI. It analyzes student attendance data and provides risk classifications, trend analysis, and personalized recommendations.

## Features

### 1. Attendance Analysis (`attendance_analysis.py`)

The `AttendanceAnalyzer` class provides:

- **Attendance Summary**: Counts of present, late, absent, half-day, and holiday records
- **Attendance Rate**: Percentage of days attended (present + late + half-day)
- **Pattern Identification**: Classifies patterns as consistent, irregular, concerning, or critical
- **Risk Classification**: AI-based risk level (excellent, good, warning, critical)
- **Trend Analysis**: Detects if attendance is improving, stable, or declining
- **Hours Tracking**: Calculates rendered vs remaining hours
- **Smart Recommendations**: Personalized action items based on risk level

### 2. FastAPI Server (`attendance_api.py`)

Provides REST API endpoints for integration with Laravel frontend:

- Health check endpoints
- Student analysis endpoints
- Risk summary and statistics
- Recommendation generation
- Data refresh capabilities

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Configuration

Ensure your MySQL database credentials in `attendance_analysis.py` match your Laravel setup:

```python
engine = create_engine('mysql+pymysql://root:@localhost/ojt_attendance_tracker')
```

Update the connection string if needed:
- Username: `root`
- Password: (leave empty or update)
- Host: `localhost`
- Database: `ojt_attendance_tracker`

## Usage

### Method 1: Direct Python Usage

```python
from attendance_analysis import AttendanceAnalyzer

# Initialize analyzer
analyzer = AttendanceAnalyzer()

# Get analysis for a specific student
student_id = "your-student-uuid"
analysis = analyzer.get_student_analysis(student_id)

# Get quick summary
summary = analyzer.get_student_attendance_summary(student_id)

# Get all students analysis
all_analysis = analyzer.get_all_students_analysis()

# Get risk summary for all students
risk_summary = analyzer.get_risk_summary()
```

### Method 2: FastAPI Server (Recommended for Integration)

#### Start the Server

```bash
python attendance_api.py
```

Or using uvicorn directly:

```bash
uvicorn attendance_api:app --reload --host 0.0.0.0 --port 8000
```

#### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```
GET /health
```
Verify the API is running.

### Student Analysis

#### Get Complete Analysis
```
GET /api/students/{student_id}/analysis
```

**Response:**
```json
{
  "student_id": "uuid",
  "student_name": "John Doe",
  "summary": {
    "total_days": 50,
    "present_count": 45,
    "late_count": 3,
    "absent_count": 2,
    "half_day_count": 0,
    "holiday_count": 0,
    "attendance_rate": 96.0,
    "pattern": "consistent"
  },
  "hours": {
    "required_hours": 240,
    "hours_rendered": 235.5,
    "remaining_hours": 4.5,
    "hours_completion_percentage": 98.13
  },
  "risk_classification": "excellent",
  "trend": {
    "trend": "stable",
    "first_half_rate": 95.0,
    "second_half_rate": 97.0,
    "change_percentage": 2.0
  },
  "recommendations": [
    "⭐ Excellent: Student demonstrates outstanding attendance and commitment.",
    "👏 Student is on track to complete all requirements."
  ]
}
```

#### Get Quick Summary
```
GET /api/students/{student_id}/summary
```

#### Get Recommendations
```
GET /api/students/{student_id}/recommendations
```

### Statistics & Risk Analysis

#### Get Risk Summary (All Students)
```
GET /api/risk-summary
```

**Response:**
```json
{
  "total_students": 50,
  "risk_distribution": {
    "excellent": 20,
    "good": 18,
    "warning": 10,
    "critical": 2
  },
  "critical_students": [
    {
      "name": "Jane Smith",
      "student_id": "uuid",
      "attendance_rate": 35.0
    }
  ]
}
```

#### Get All Students Analysis
```
GET /api/students/analysis/all
```

#### Get Overall Statistics
```
GET /api/statistics?time_period=all
```

### Maintenance

#### Refresh Analysis Data
```
POST /api/analysis/refresh
```
Forces reload of data from database.

## Risk Classification Logic

Students are classified into risk levels based on:

1. **Attendance Rate** (40% weight): Percentage of days attended
2. **Absence Count** (30% weight): Number of absences relative to period
3. **Hours Completion** (30% weight): Progress toward required hours

**Classification Scale:**
- **Excellent** (80-100): Outstanding performance, on track
- **Good** (60-79): Acceptable performance, monitor if declining
- **Warning** (40-59): Below acceptable, intervention needed
- **Critical** (0-39): Severe issues, immediate action required

## Pattern Types

- **Consistent**: 90%+ attendance rate - reliable and dependable
- **Irregular**: 70-89% attendance rate - mostly reliable with some gaps
- **Concerning**: 50-69% attendance rate - significant attendance issues
- **Critical**: <50% attendance rate - severe attendance problems

## Trend Analysis

The system compares attendance in the first half of the period with the second half:

- **Improving**: Second half rate is 5%+ higher
- **Stable**: Difference is less than 5%
- **Declining**: Second half rate is 5%+ lower

## Integration with Laravel

### From Laravel Blade/Vue:

```javascript
// Get student analysis
async function getStudentAnalysis(studentId) {
  const response = await fetch(`http://localhost:8000/api/students/${studentId}/analysis`);
  const data = await response.json();
  return data;
}

// Get risk summary
async function getRiskSummary() {
  const response = await fetch('http://localhost:8000/api/risk-summary');
  const data = await response.json();
  return data;
}
```

### CORS Configuration

The API is configured with CORS enabled for all origins. For production, update `attendance_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Database Schema

The system expects these tables (created by Laravel migrations):

### Students Table
```sql
- id (UUID, Primary Key)
- name (String)
- required_hours (Integer)
- start_date (Date)
- end_date (Date)
```

### Attendances Table
```sql
- id (UUID, Primary Key)
- student_id (UUID, Foreign Key)
- date (Date)
- time_in (Time)
- time_out (Time)
- status (Enum: present, late, absent, half_day, holiday)
- hours_rendered (Decimal)
```

## Examples

### Example 1: Monitor At-Risk Students

```python
from attendance_analysis import AttendanceAnalyzer

analyzer = AttendanceAnalyzer()
risk_summary = analyzer.get_risk_summary()

print("Critical Students:")
for student in risk_summary['critical_students']:
    print(f"- {student['name']}: {student['attendance_rate']}% attendance")
```

### Example 2: Generate Student Report

```python
analyzer = AttendanceAnalyzer()
analysis = analyzer.get_student_analysis("student-uuid")

print(f"Student: {analysis['student_name']}")
print(f"Risk Level: {analysis['risk_classification']}")
print(f"Attendance Rate: {analysis['summary']['attendance_rate']}%")
print(f"Hours Completed: {analysis['hours']['hours_rendered']} / {analysis['hours']['required_hours']}")
print("\nRecommendations:")
for rec in analysis['recommendations']:
    print(f"  {rec}")
```

### Example 3: API Call from JavaScript

```javascript
// Get analysis for a student
fetch('http://localhost:8000/api/students/some-uuid/analysis')
  .then(response => response.json())
  .then(data => {
    console.log(`Risk Level: ${data.risk_classification}`);
    console.log(`Attendance: ${data.summary.attendance_rate}%`);
    console.log(`Recommendations:`, data.recommendations);
  });
```

## Troubleshooting

### Issue: "Student not found"
- Verify the student_id UUID is correct
- Check that the student exists in the database

### Issue: "Connection refused to MySQL"
- Ensure MySQL is running
- Check database credentials in `attendance_analysis.py`
- Verify database name is correct

### Issue: API not responding
- Check that uvicorn server is running
- Verify port 8000 is not in use
- Check firewall settings

### Issue: No attendance data
- Verify attendance records exist in the database
- Use `/api/statistics` to check total records
- Run `/api/analysis/refresh` to reload data

## Performance Considerations

- Data is loaded fresh on each request to ensure accuracy
- For high-volume systems, consider caching with Redis
- Pagination can be added to `get_all_students_analysis()` for large datasets
- Database indexing on `student_id` and `date` is recommended

## Future Enhancements

- [ ] Predictive models for attendance forecasting
- [ ] Custom alert thresholds
- [ ] Export reports to PDF/Excel
- [ ] Historical trend charts
- [ ] Comparative analysis between students
- [ ] Integration with email notifications
- [ ] Advanced time-series analysis
- [ ] Machine learning models for pattern prediction

## Support

For issues or questions, check:
1. Database connectivity
2. Table structure matches expectations
3. Student and attendance records exist
4. API logs for detailed error messages
5. Database credentials are correct
