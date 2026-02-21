<?php

namespace App\Http\Controllers;
use App\Models\Attendance;
use App\Models\Student;
use Carbon\Carbon;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\Log;



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
            'time_out' => 'required|date_format:H:i', 
            'status' => 'required|string|in:present,absent,late,half_day,holiday',
        ]);

        // Fetch the student to check shift times for late status
        $student = Student::find($validated['student_id'] ?? null);

        if(!$student){
            return response()->json([
                'message' => 'Student not found'
            ], 404);
        }

        // Validate that time_out is after time_in
        $timeIn = Carbon::createFromFormat('H:i', $validated['time_in']);
        $timeOut = Carbon::createFromFormat('H:i', $validated['time_out']);

        $adjustedTimeOut = $timeOut->copy();

        // Handle midnight crossover 
        if ($adjustedTimeOut->lessThan($timeIn) && ($student->shift_name === 'Afternoon' || $student->shift_name === 'Evening')) {
            $adjustedTimeOut->addDay();
        }

        // Validate: time_out cannot equal time_in
        if ($adjustedTimeOut->lessThanOrEqualTo($timeIn)) {
            return response()->json([
                'message' => 'Time out must be after time in',
                'errors' => ['time_out' => ['Time out must be after time in']]
            ], 422);
        }

        // If student exists and time_in is after shift_start, mark as late
        if ($student && $student->shift_start && isset($validated['time_in']) && $validated['status'] === 'present') {
            try {
                $shiftStart = Carbon::createFromFormat('H:i', $student->shift_start);
                if ($timeIn->gt($shiftStart)) {
                    $validated['status'] = 'late';
                }
            } catch (\Exception $e) {
                // If shift_start parsing fails, skip the late check
                // The record will still be saved with the provided status
            }
        }

        // Calculate hours_rendered automatically
        $hours_rendered = 0;

        if (in_array($validated['status'], ['present', 'late'])) {

            $hours = $timeIn->diffInMinutes($adjustedTimeOut) / 60 - 1; // subtract 1 hour for lunch break
            $hours_rendered = max(0, $hours); // ensure not negative

        } elseif ($validated['status'] === 'half_day') {

            $hours_rendered = 4;

        } else { // absent or holiday

            $hours_rendered = 0;
            
        }

        Log::info('Hours calculation debug', [
            'timeIn' => $timeIn->format('H:i'),
            'timeOut' => $timeOut->format('H:i'),
            'adjustedTimeOut' => $adjustedTimeOut->format('H:i'),
            'totalMinutes' => $adjustedTimeOut->diffInMinutes($timeIn),
            'totalHours' => $adjustedTimeOut->diffInMinutes($timeIn) / 60,
            'hoursAfterLunchDeduction' => ($adjustedTimeOut->diffInMinutes($timeIn) / 60) - 1,
            'status' => $validated['status'],
            'shift_name' => $student->shift_name ?? 'null',
        ]);


        // Handle potential database errors gracefully
        try{
            $attendance = Attendance::create(array_merge($validated, ['hours_rendered' => $hours_rendered])); // create attendance record with calculated hours
            
            return response()->json([
                'message' => 'attendance recorded successfully',
                'data' => $attendance
            ], 201);

        }catch (QueryException $e){

            // Check for duplicate entry error (SQLSTATE 23000) which occurs when trying to create an attendance record for the same student on the same date
            if ($e->getCode() == 23000) {
                return response()->json([
                    'message' => 'Attendance for this student on this date already exists.'
                ], 422);
            }

            return response()->json([
                'message' => 'Something went wrong. Please try again.'
            ], 500);
        }

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
            'student_id' => 'sometimes|exists:students,id',
            'date' => 'sometimes|date',
            'time_in' => 'sometimes|date_format:H:i',
            'time_out' => 'sometimes|date_format:H:i',
            'status' => 'sometimes|string|in:present,absent,late,half_day,holiday',
        ]);

        $student = $attendance->student;

        // Check for duplicate date if date is being updated
        if (isset($validated['date']) && $validated['date'] !== $attendance->date) { 
            $exists = Attendance::where('student_id', $student->id)
                ->where('date', $validated['date'])
                ->where('id', '!=', $attendance->id)
                ->exists();

            if ($exists) {
                return response()->json([
                    'message' => 'Attendance for this student on this date already exists.'
                ], 422);
            }
        }

         // If student exists and time_in is after shift_start, mark as late
        if ($student && $student->shift_start && isset($validated['time_in']) && (isset($validated['status']) ? $validated['status'] : $attendance->status) === 'present') { 
            try {
                $timeIn = Carbon::createFromFormat('H:i', $validated['time_in'] ?? $attendance->time_in);
                $shiftStart = Carbon::createFromFormat('H:i', $student->shift_start);

                if ($timeIn->gt($shiftStart)) {
                    $validated['status'] = 'late';
                }
            } catch (\Exception $e) {
                // If shift_start parsing fails, skip the late check
                // The record will still be saved with the provided status
            }
        }

        // Calculate hours_rendered if time_in, time_out, or status is being updated
        if (isset($validated['time_in']) || isset($validated['time_out']) || isset($validated['status'])) {
            $timeIn = isset($validated['time_in']) ? $validated['time_in'] : $attendance->time_in;
            $timeOut = isset($validated['time_out']) ? $validated['time_out'] : $attendance->time_out;
            $status = isset($validated['status']) ? $validated['status'] : $attendance->status;

            $timeInObj = Carbon::createFromFormat('H:i', $timeIn);
            $timeOutObj = Carbon::createFromFormat('H:i', $timeOut);

            $adjustedTimeOut = $timeOutObj->copy();

            // Handle midnight crossover for Afternoon and Evening shifts
            if ($adjustedTimeOut->lessThan($timeInObj) && 
                ($student->shift_name === 'Afternoon' || $student->shift_name === 'Evening')) {
                $adjustedTimeOut->addDay();
            }

            // Validate that time_out is after time_in
            if ($adjustedTimeOut->lessThanOrEqualTo($timeInObj)) {
                return response()->json([
                    'message' => 'Time out must be after time in',
                    'errors' => ['time_out' => ['Time out must be after time in']]
                ], 422);
            }

            // Calculate hours_rendered using adjustedTimeOut for shifts that cross midnight
            $hours_rendered = 0;
            if (in_array($status, ['present', 'late'])) {
                $hours = $timeInObj->diffInMinutes($adjustedTimeOut) / 60 - 1; // Subtract 1 hour for lunch break
                $hours_rendered = max(0, $hours);
            } elseif ($status === 'half_day') {
                $hours_rendered = 4;
            } else { // absent or holiday
                $hours_rendered = 0;
            }

            $validated['hours_rendered'] = $hours_rendered;
        }

        $attendance->update($validated);

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
