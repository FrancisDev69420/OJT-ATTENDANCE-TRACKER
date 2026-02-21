<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Student extends Model
{

    protected $keyType = 'string'; // Set the primary key type to string for UUID
    public $incrementing = false; // Disable auto-incrementing since we're using UUIDs

    protected $fillable = [
        'name',
        'required_hours',
        'start_date',
        'end_date',
        'shift_start',
        'shift_end',
        'shift_name',
    ];

    protected function casts(): array
    {
        return [
            'id' => 'string',
            'start_date' => 'date',
            'end_date' => 'date',
            'shift_start' => 'datetime:H:i',
            'shift_end' => 'datetime:H:i',
        ];
    }

    protected static function boot(){
        parent::boot();

        static::creating(function ($model) {
            $model->id = (string) Str::uuid();
        });
    }

    // Use UUID for route model binding
    public function getRouteKeyName(){
        return 'id';
    }

    public function attendances(){
        return $this->hasMany(Attendance::class);
    }
}
