<?php

namespace App\Http\Controllers;
use App\Models\Student;
use Carbon\Carbon;
use Illuminate\Support\Facades\Storage;

use Illuminate\Http\Request;

class StudentController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $students = Student::all();

        return response()->json([
            'message' => 'All Students retrieved successfully',
            'data' => $students
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'required_hours' => 'required|integer',
            'start_date' => 'required|date',
            'end_date' => 'required|date|after_or_equal:start_date',
            'shift_start' => 'nullable|date_format:H:i',
            'shift_end' => 'nullable|date_format:H:i',
            'shift_name' => 'nullable|string|max:255',
            'profile_picture' => 'nullable|string', 
        ]);

        // Validate shift times with midnight crossover support for Afternoon and Evening shifts
        if (isset($validated['shift_start']) && isset($validated['shift_end'])) {
            $shiftStart = Carbon::createFromFormat('H:i', $validated['shift_start']);
            $shiftEnd = Carbon::createFromFormat('H:i', $validated['shift_end']);
            
            $adjustedShiftEnd = $shiftEnd->copy();
            
            // Handle midnight crossover for Afternoon and Evening shifts
            if ($adjustedShiftEnd->lessThan($shiftStart) && 
                (isset($validated['shift_name']) && 
                 ($validated['shift_name'] === 'Afternoon' || $validated['shift_name'] === 'Evening'))) {
                $adjustedShiftEnd->addDay();
            }
            
            // Validate that shift_end is after shift_start
            if ($adjustedShiftEnd->lessThanOrEqualTo($shiftStart)) {
                return response()->json([
                    'message' => 'Shift end time must be after shift start time',
                    'errors' => ['shift_end' => ['Shift end time must be after shift start time']]
                ], 422);
            }
        }
        
        $studentData = collect($validated)->except('profile_picture')->toArray(); // Exclude profile_picture from mass assignment
        $student = Student::create($studentData);

        // Handle profile picture upload if provided
        if ($request->profile_picture) {
            $imageData = base64_decode(preg_replace('#^data:image/\w+;base64,#i', '', $request->profile_picture));
            $filename = $student->fresh()->id . '_' . time() . '.png'; // fresh() re-fetches from DB

            Storage::put('private/profile_pictures/' . $filename, encrypt($imageData));

            $student->profile_picture = 'private/profile_pictures/' . $filename;
            $student->save();
        }

        return response()->json([
            'message' => 'Student created successfully: ' . $student->name . ' (' . $student->id . ')',
            'data' => $student
        ], 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(Student $student)
    {
        return response()->json([
            'message' => 'Student retrieved successfully',
            'data' => $student
        ], 200);
    }
    

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Student $student)
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'required_hours' => 'sometimes|integer',
            'start_date' => 'sometimes|date',
            'end_date' => 'sometimes|date|after_or_equal:start_date',
            'shift_start' => 'sometimes|date_format:H:i',
            'shift_end' => 'sometimes|date_format:H:i',
            'shift_name' => 'sometimes|string|max:255',
        ]);

        // Validate shift times with midnight crossover support for Afternoon and Evening shifts
        if (isset($validated['shift_start']) || isset($validated['shift_end']) || isset($validated['shift_name'])) {
            $shiftStart = isset($validated['shift_start']) ? $validated['shift_start'] : $student->shift_start;
            $shiftEnd = isset($validated['shift_end']) ? $validated['shift_end'] : $student->shift_end;
            $shiftName = isset($validated['shift_name']) ? $validated['shift_name'] : $student->shift_name;
            
            if ($shiftStart && $shiftEnd) {
                $shiftStartObj = Carbon::createFromFormat('H:i', $shiftStart);
                $shiftEndObj = Carbon::createFromFormat('H:i', $shiftEnd);
                
                $adjustedShiftEnd = $shiftEndObj->copy();
                
                // Handle midnight crossover for Afternoon and Evening shifts
                if ($adjustedShiftEnd->lessThan($shiftStartObj) && 
                    ($shiftName === 'Afternoon' || $shiftName === 'Evening')) {
                    $adjustedShiftEnd->addDay();
                }
                
                // Validate that shift_end is after shift_start
                if ($adjustedShiftEnd->lessThanOrEqualTo($shiftStartObj)) {
                    return response()->json([
                        'message' => 'Shift end time must be after shift start time',
                        'errors' => ['shift_end' => ['Shift end time must be after shift start time']]
                    ], 422);
                }
            }
        }

        $student->update($validated);

        return response()->json([
            'message' => 'Student updated successfully',
            'data' => $student
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Student $student)
    {
        $student->delete();

        return response()->json([
            'message' => 'Student deleted successfully',
        ], 200);
    }

    // // Upload profile picture for a student
    // public function uploadProfilePicture(Request $request, Student $student) 
    // {
    //     // Validate the uploaded file
    //     $validated = $request->validate([
    //         'profile_picture' => 'required|image|max:2048', // Max 2MB
    //     ]);

    //     if ($request->hasFile('profile_picture')) { 

    //         $file = $request->file('profile_picture');
    //         $filename = $student->id . '_' . time() . '.' . $file->getClientOriginalExtension();

    //         // Store the file in a private directory and encrypt it
    //         Storage::put('private/profile_pictures/' . $filename, encrypt(file_get_contents($file)));

    //         // Update the student's profile picture path in the database
    //         $student->profile_picture = 'private/profile_pictures/' . $filename;
    //         $student->save();

    //         return response()->json([
    //             'message' => 'Profile picture uploaded successfully',
    //             'data' => ['profile_picture' => $filename]
    //         ], 200);
    //     }

    //     return response()->json([
    //         'message' => 'No profile picture uploaded',
    //     ], 400);
    // }

    // Get profile picture for a student
    public function getProfilePicture(Student $student){

        $path = $student->profile_picture;

        if(!Storage::exists($path)){
            return response()->json([
                'message' => 'Profile picture not found',
            ], 404);
        }

        // Decrypt the file content before returning it
        $content = decrypt(Storage::get($path));

        // Return the file content with appropriate headers
        return response($content, 200)->header('Content-Type', mime_content_type(storage_path('app/' . $path))); 

    }
}
