<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>{{ isEditMode ? 'Edit Attendance' : 'Record Attendance' }}</h3>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <form @submit.prevent="submitForm">
          <!-- Date Field -->
          <div class="form-group">
            <label for="date">Date *</label>
            <input
              id="date"
              v-model="form.date"
              type="date"
              required
              class="form-control"
            />
          </div>

          <!-- Time In -->
          <div class="form-group">
            <label for="time_in">Time In *</label>
            <input
              id="time_in"
              v-model="form.time_in"
              type="time"
              required
              class="form-control"
            />
          </div>

          <!-- Time Out -->
          <div class="form-group">
            <label for="time_out">Time Out *</label>
            <input
              id="time_out"
              v-model="form.time_out"
              type="time"
              required
              class="form-control"
            />
          </div>

          <!-- Status -->
          <div class="form-group">
            <label for="status">Status *</label>
            <select
              id="status"
              v-model="form.status"
              required
              class="form-control"
            >
              <option value="">Select Status</option>
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="late">Late</option>
              <option value="half_day">Half Day</option>
              <option value="holiday">Holiday</option>
            </select>
          </div>

          <!-- Validation Messages -->
          <div v-if="validationErrors && Object.keys(validationErrors).length > 0" class="validation-errors">
            <p v-for="(messages, field) in validationErrors" :key="field">
              <strong>{{ capitalizeField(field) }}:</strong> {{ messages.join(', ') }}
            </p>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>

          <!-- Form Buttons -->
          <div class="form-actions">
            <button
              type="submit"
              :disabled="isSubmitting"
              class="btn btn-primary"
            >
              {{ isSubmitting ? (isEditMode ? 'Updating...' : 'Submitting...') : (isEditMode ? 'Update Attendance' : 'Record Attendance') }}
            </button>
            <button
              type="button"
              @click="closeModal"
              class="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AttendanceForm',
  props: {
    apiBaseUrl: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isOpen: false,
      studentId: null,
      attendanceId: null,
      isEditMode: false,
      form: {
        date: '',
        time_in: '',
        time_out: '',
        status: '',
      },
      isSubmitting: false,
      error: null,
      successMessage: null,
      validationErrors: null,
    };
  },
  methods: {
    openModal(studentId, attendanceRecord = null) {
      this.studentId = studentId;
      this.isOpen = true;
      this.error = null;
      this.successMessage = null;

      // Parse dates to yyyy-MM-dd format for date input
      const parseDate = (dateString) => {
        if (!dateString) return '';
        try {
          const date = new Date(dateString);
          if (isNaN(date.getTime())) return '';
          return date.toISOString().split('T')[0];
        } catch (e) {
          console.error('Error parsing date:', e);
          return '';
        }
      };

      if (attendanceRecord) {
        // Edit mode
        this.isEditMode = true;
        this.attendanceId = attendanceRecord.id;
        this.form = {
          date: parseDate(attendanceRecord.date),
          time_in: attendanceRecord.time_in,
          time_out: attendanceRecord.time_out,
          status: attendanceRecord.status,
        };
      } else {
        // Create mode
        this.isEditMode = false;
        this.attendanceId = null;
        this.resetForm();
      }
    },
    closeModal() {
      this.isOpen = false;
      this.resetForm();
      this.error = null;
      this.successMessage = null;
      this.validationErrors = null;
    },
    resetForm() {
      this.form = {
        date: '',
        time_in: '',
        time_out: '',
        status: '',
      };
    },
    async submitForm() {
      if (!this.studentId) {
        this.error = 'Student ID is missing';
        return;
      }

      try {
        this.isSubmitting = true;
        this.error = null;
        this.validationErrors = null;
        this.successMessage = null;

        const payload = {
          student_id: this.studentId,
          date: this.form.date,
          time_in: this.form.time_in,
          time_out: this.form.time_out,
          status: this.form.status,
        };

        let response;

        if (this.isEditMode && this.attendanceId) {
          // Update existing attendance
          console.log('Updating attendance:', this.attendanceId, payload);
          response = await axios.put(
            `${this.apiBaseUrl}/attendances/${this.attendanceId}`,
            payload
          );
          this.successMessage = 'Attendance updated successfully!';
        } else {
          // Create new attendance
          console.log('Submitting attendance form:', payload);
          response = await axios.post(
            `${this.apiBaseUrl}/attendances`,
            payload
          );
          this.successMessage = 'Attendance recorded successfully!';
        }

        console.log('Attendance response:', response.data);

        // Reset form and close after 1.5 seconds
        setTimeout(() => {
          this.$emit('attendance-saved', response.data.data);
          this.closeModal();
        }, 1500);
      } catch (error) {
        console.error('Error submitting attendance:', error);

        if (error.response && error.response.status === 422) {

          // Handle validation errors
          if (error.response.data.errors) {
            this.validationErrors = error.response.data.errors;
          } else if (error.response.data.message) {
            this.error = error.response.data.message;  
          } else {
            this.error = 'Validation failed. Please check your input.';
          }

        } else if (error.response && error.response.data && error.response.data.message) {
          this.error = error.response.data.message;
        } else {
          this.error = this.isEditMode ? 'Failed to update attendance. Please try again.' : 'Failed to record attendance. Please try again.';
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    capitalizeField(field) {
      return field
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },
  },
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: #ff8c42;
  box-shadow: 0 0 0 3px rgba(255, 140, 42, 0.1);
}

.form-control select {
  cursor: pointer;
}

.error-message {
  padding: 12px 16px;
  background-color: #fee;
  color: #c33;
  border-left: 4px solid #c33;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.success-message {
  padding: 12px 16px;
  background-color: #efe;
  color: #3c3;
  border-left: 4px solid #3c3;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 14px;
}

.validation-errors {
  padding: 12px 16px;
  background-color: #fff3cd;
  color: #856404;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 13px;
}

.validation-errors p {
  margin: 0 0 8px 0;
}

.validation-errors p:last-child {
  margin-bottom: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #ff8c42;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e67e2f;
  box-shadow: 0 4px 12px rgba(255, 140, 42, 0.3);
}

.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
}

.btn-secondary:hover {
  background-color: #e8e8e8;
}

@media (max-width: 600px) {
  .modal-content {
    width: 95%;
    max-width: none;
  }

  .modal-header,
  .modal-body {
    padding: 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
