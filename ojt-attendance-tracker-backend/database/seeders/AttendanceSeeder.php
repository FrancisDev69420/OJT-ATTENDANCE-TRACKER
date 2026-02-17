<?php

namespace Database\Seeders;

use App\Models\Attendance;
use Carbon\Carbon;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Str;

class AttendanceSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed attendance records for a student.
     */
    public function run(): void
    {
        $studentId = '8ace60ec-1ffb-4323-8785-7b5b11e5c446';
        $startDate = Carbon::createFromFormat('Y-m-d', '2026-01-27');
        
        // Generate 20 days of attendance records
        for ($i = 0; $i < 20; $i++) {
            $currentDate = $startDate->copy()->addDays($i);
            
            // Skip weekends (Saturday=6, Sunday=0)
            if ($currentDate->dayOfWeek === 0 || $currentDate->dayOfWeek === 6) {
                continue;
            }
            
            // Vary the status: mostly present, some late, occasional absent
            $statuses = ['present', 'present', 'present', 'present', 'late', 'late', 'absent', 'half_day'];
            $status = $statuses[array_rand($statuses)];
            
            // Generate time_in and time_out
            if ($status === 'absent') {
                $timeIn = null;
                $timeOut = null;
                $hoursRendered = 0.0;
            } elseif ($status === 'half_day') {
                $timeIn = '08:00';
                $timeOut = '12:00';
                $hoursRendered = 4.0;
            } elseif ($status === 'late') {
                $timeIn = '09:00'; // Late arrival
                $timeOut = '17:00';
                $hoursRendered = 8.0;
            } else { // present
                $timeIn = '08:00';
                $timeOut = '17:00';
                $hoursRendered = 9.0;
            }
            
            Attendance::create([
                'id' => (string) Str::uuid(),
                'student_id' => $studentId,
                'date' => $currentDate,
                'time_in' => $timeIn,
                'time_out' => $timeOut,
                'status' => $status,
                'hours_rendered' => $hoursRendered,
            ]);
        }
        
        $this->command->info('Successfully created 20 attendance records for student ' . $studentId);
    }
}
