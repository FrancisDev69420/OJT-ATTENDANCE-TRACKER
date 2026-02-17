<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\StudentController;
use App\Http\Controllers\AttendanceController;

Route::middleware('api')->group(function () {
    // Student Routes (RESTful Resource)
    Route::apiResource('students', StudentController::class);

    // Attendance Routes (RESTful Resource)
    Route::apiResource('attendances', AttendanceController::class);

    // Attendance routes nested under students
    Route::get('/students/{student}/attendances', [AttendanceController::class, 'show']);
    Route::get('/students/{student}/remaining-hours', [AttendanceController::class, 'remainingHours']);
});