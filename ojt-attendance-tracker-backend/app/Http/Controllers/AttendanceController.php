<?php

namespace App\Http\Controllers;
use App\Models\Attendance;
use App\Models\Student;


use Illuminate\Http\Request;

class AttendanceController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $attendances = Attendance::all();

        return response()->json([
            'message' => 'All attendance retrieved successfully',
            'data' => $attendances
        ], 200);
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'student_id' => 'required|exists:students,id', // validate UUID
            'date' => 'required|date',
            'time_in' => 'required|date_format:H:i',
            'time_out' => 'required|date_format:H:i|after:time_in',
            'status' => 'required|string|in:present,absent,late,half_day,holiday',
        ]);

        // Calculate hours_rendered automatically
        if (in_array($validated['status'], ['present', 'late'])) {
            $hours_rendered = (strtotime($validated['time_out']) - strtotime($validated['time_in'])) / 3600 - 1; // convert seconds to hours and subtract 1 hour for lunch break
        } elseif ($validated['status'] === 'half_day') {
            $hours_rendered = 4;
        } else { // absent or holiday
            $hours_rendered = 0;
        }


        $attendance = Attendance::create(array_merge($validated, ['hours_rendered' => $hours_rendered])); // create attendance record with calculated hours

        return response()->json([
           'message' => 'attendance recorded successfully',
            'data' => $attendance
        ], 201);
    }

    // Display remaining hours for a student
    public function remainingHours(Student $student)
    {
        $totalHours = $student->attendances()->sum('hours_rendered');
        $remainingHours = max(0, $student->required_hours - $totalHours); // Calculates and Ensure remaining hours doesn't go negative

        return response()->json([
            'message' => 'Remaining hours calculated successfully',
            'data' => [
                'total_hours_rendered' => $totalHours,
                'remaining_hours' => $remainingHours,
            ]
        ], 200);
    }

    /**
     * Display the specified resource.
     */
    public function show(Student $student)
    {
        $attendances = $student->attendances()->get();

        return response()->json([
            'message' => 'Student attendance records retrieved successfully',
            'data' => $attendances
        ], 200);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
    {
        
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Attendance $attendance)
    {
         $validated = $request->validate([
            'student_id' => 'sometimes|exists:students,id', // validate UUID
            'date' => 'sometimes|date',
            'time_in' => 'sometimes|date_format:H:i',
            'time_out' => 'sometimes|date_format:H:i|after:time_in',
            'status' => 'sometimes|string|in:present,absent,late,half_day,holiday',
        ]);

        // Calculate hours_rendered automatically
        if (in_array($validated['status'], ['present', 'late'])) {
            $hours_rendered = (strtotime($validated['time_out']) - strtotime($validated['time_in'])) / 3600; // convert seconds to hours
        } elseif ($validated['status'] === 'half_day') {
            $hours_rendered = 4;
        } else { // absent
            $hours_rendered = 0;
        }

        $attendance->update(array_merge($validated, ['hours_rendered' => $hours_rendered])); // update attendance record with calculated hours

        return response()->json([
            'message' => 'Student attendance records updated successfully',
            'data' => $attendance
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Attendance $attendance)
    {
        $attendance->delete();

        return response()->json([
            'message' => 'Attendance record deleted successfully',
        ], 200);
    }
}
