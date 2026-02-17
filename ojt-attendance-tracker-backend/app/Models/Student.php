<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Student extends Model
{
    protected $fillable = [
        'name',
        'required_hours',
        'start_date',
        'end_date',
    ];

    protected function casts(): array
    {
        return [
            'id' => 'string',
            'start_date' => 'date',
            'end_date' => 'date',
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
