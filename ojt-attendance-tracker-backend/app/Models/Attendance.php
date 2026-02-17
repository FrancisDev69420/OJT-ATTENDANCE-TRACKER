<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Attendance extends Model
{
    protected $fillable = [
        'student_id',
        'date',
        'time_in',
        'time_out',
        'status',
        'hours_rendered',
    ];

    protected function casts(): array
    {
        return [
            'date' => 'date',
            'time_in' => 'datetime:H:i', // 24 hour format
            'time_out' => 'datetime:H:i',
        ];
    }

    protected static function boot()
    {
        parent::boot();

        static::creating(function ($model) {
            $model->id = (string) Str::uuid();
        });
    }

    // Attendance belongs to a student
    public function student()
    {
        return $this->belongsTo(Student::class);
    }
}
