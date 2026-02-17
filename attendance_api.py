"""
FastAPI Server for Attendance Analysis

Provides REST API endpoints to connect with Laravel backend.
Serves attendance analysis data and integrates with the database.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging

from attendance_analysis import AttendanceAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Attendance Analysis API",
    description="AI-powered attendance pattern analysis API for OJT Attendance Tracker",
    version="1.0.0"
)

# Add CORS middleware for Laravel frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],  # Development origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = AttendanceAnalyzer()


# Pydantic Models for request/response validation
class StudentAnalysisResponse(BaseModel):
    """Response model for student analysis"""
    student_id: str
    student_name: str
    summary: Dict
    hours: Dict
    risk_classification: str
    trend: Dict
    recommendations: List[str]


class RiskSummaryResponse(BaseModel):
    """Response model for risk summary"""
    total_students: int
    risk_distribution: Dict
    critical_students: List[Dict]


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status of the API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Attendance Analysis API"
    }


# Attendance Analysis Endpoints
@app.get("/api/students/{student_id}/analysis", tags=["Analysis"], response_model=StudentAnalysisResponse)
async def get_student_analysis(student_id: str):
    """
    Get comprehensive analysis for a specific student.
    
    Args:
        student_id: UUID of the student
        
    Returns:
        StudentAnalysisResponse: Complete analysis including risk classification, hours, trends, and recommendations
        
    Raises:
        HTTPException: If student not found or analysis fails
    """
    try:
        analysis = analyzer.get_student_analysis(student_id)
        
        if 'error' in analysis:
            raise HTTPException(status_code=404, detail=analysis['error'])
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing student: {str(e)}")


@app.get("/api/students/{student_id}/summary", tags=["Analysis"])
async def get_student_summary(student_id: str):
    """
    Get quick attendance summary for a specific student.
    
    Args:
        student_id: UUID of the student
        
    Returns:
        dict: Attendance counts and rates
    """
    try:
        summary = analyzer.get_student_attendance_summary(student_id)
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        logger.error(f"Error getting summary for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@app.get("/api/risk-summary", tags=["Analysis"], response_model=RiskSummaryResponse)
async def get_risk_summary():
    """
    Get risk classification summary for all students.
    
    Returns:
        RiskSummaryResponse: Distribution of students by risk level and critical students list
    """
    try:
        summary = analyzer.get_risk_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting risk summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting risk summary: {str(e)}")


@app.get("/api/students/analysis/all", tags=["Analysis"])
async def get_all_students_analysis():
    """
    Get analysis for all students.
    
    Returns:
        dict: List of analysis for all students
    """
    try:
        all_analysis = analyzer.get_all_students_analysis()
        return {
            "status": "success",
            "total_students": len(all_analysis),
            "data": all_analysis
        }
    except Exception as e:
        logger.error(f"Error getting all analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting analyses: {str(e)}")


@app.get("/api/statistics", tags=["Statistics"])
async def get_statistics(time_period: Optional[str] = Query(None, description="Time period: week, month, all")):
    """
    Get overall attendance statistics.
    
    Args:
        time_period: Optional filter for time period (week, month, all)
        
    Returns:
        dict: Overall statistics
    """
    try:
        analyzer.load_data()
        
        attendances_df = analyzer.attendances_df
        students_df = analyzer.students_df
        
        total_students = len(students_df)
        total_attendance_records = len(attendances_df)
        
        # Status breakdown
        status_breakdown = attendances_df['status'].value_counts().to_dict()
        
        # Average attendance rate
        avg_hours = attendances_df['hours_rendered'].mean()
        total_hours = attendances_df['hours_rendered'].sum()
        
        return {
            "status": "success",
            "data": {
                "total_students": total_students,
                "total_attendance_records": total_attendance_records,
                "status_breakdown": status_breakdown,
                "average_hours_rendered": round(avg_hours, 2),
                "total_hours_rendered": round(total_hours, 2),
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@app.post("/api/analysis/refresh", tags=["Maintenance"])
async def refresh_analysis():
    """
    Force refresh of analysis data from database.
    
    Useful when new attendance records are added to the database.
    
    Returns:
        dict: Status of refresh operation
    """
    try:
        analyzer.load_data()
        return {
            "status": "success",
            "message": "Analysis data refreshed successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing analysis: {str(e)}")


@app.get("/api/students/{student_id}/recommendations", tags=["Analysis"])
async def get_student_recommendations(student_id: str):
    """
    Get personalized recommendations for a student based on their attendance pattern.
    
    Args:
        student_id: UUID of the student
        
    Returns:
        dict: Recommendations and action items
    """
    try:
        analysis = analyzer.get_student_analysis(student_id)
        
        if 'error' in analysis:
            raise HTTPException(status_code=404, detail=analysis['error'])
        
        return {
            "status": "success",
            "student_id": student_id,
            "student_name": analysis['student_name'],
            "risk_classification": analysis['risk_classification'],
            "recommendations": analysis['recommendations']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API documentation link"""
    return {
        "message": "Attendance Analysis API",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc"
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    # Default: http://localhost:8000
    # Docs: http://localhost:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8001)
