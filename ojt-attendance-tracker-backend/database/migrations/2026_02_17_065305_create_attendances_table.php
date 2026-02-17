<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('attendances', function (Blueprint $table) {
            $table->uuid('id')->primary(); // Attendance UUID primary key

            $table->uuid('student_id'); // UUID column
            $table->foreign('student_id')  // Foreign key
                ->references('id')
                ->on('students')
                ->onDelete('cascade');

            $table->date('date');
            $table->time('time_in')->nullable();
            $table->time('time_out')->nullable();
            $table->enum('status', ['present', 'late', 'absent', 'half_day', 'holiday']);
            $table->decimal('hours_rendered', 5, 2)->default(0);

            $table->timestamps();

            $table->unique(['student_id', 'date']); // prevent duplicate attendance per day
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('attendances');
    }
};
