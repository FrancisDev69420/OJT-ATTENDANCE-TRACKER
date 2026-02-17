<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-title">
          <h2>{{ isEditMode ? 'Edit Student' : 'Add New Student' }}</h2>
          <p class="form-subtitle">{{ isEditMode ? 'Update student information' : 'Register a new student in the system' }}</p>
        </div>
        <button class="btn-close" @click="closeModal" aria-label="Close modal">
          ✕
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="form-content">
          <!-- Name Input -->
          <div class="form-group">
            <label for="name" class="form-label">
              <span class="label-text">Student Name</span>
              <span class="required-asterisk">*</span>
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.name }"
              placeholder="Enter student full name"
              required
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>

          <!-- Required Hours Input -->
          <div class="form-group">
            <label for="required_hours" class="form-label">
              <span class="label-text">Required Hours</span>
              <span class="required-asterisk">*</span>
            </label>
            <input
              id="required_hours"
              v-model.number="formData.required_hours"
              type="number"
              class="form-input"
              :class="{ 'input-error': errors.required_hours }"
              placeholder="e.g., 400"
              min="1"
              required
            />
            <span v-if="errors.required_hours" class="error-message">{{ errors.required_hours }}</span>
          </div>

          <!-- Start Date Input -->
          <div class="form-group">
            <label for="start_date" class="form-label">
              <span class="label-text">Start Date</span>
              <span class="required-asterisk">*</span>
            </label>
            <input
              id="start_date"
              v-model="formData.start_date"
              type="date"
              class="form-input"
              :class="{ 'input-error': errors.start_date }"
              required
            />
            <span v-if="errors.start_date" class="error-message">{{ errors.start_date }}</span>
          </div>

          <!-- End Date Input -->
          <div class="form-group">
            <label for="end_date" class="form-label">
              <span class="label-text">End Date</span>
              <span class="required-asterisk">*</span>
            </label>
            <input
              id="end_date"
              v-model="formData.end_date"
              type="date"
              class="form-input"
              :class="{ 'input-error': errors.end_date }"
              required
            />
            <span v-if="errors.end_date" class="error-message">{{ errors.end_date }}</span>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="success-message">
            <span class="success-icon">✓</span>
            {{ successMessage }}
          </div>

          <!-- Error Message -->
          <div v-if="generalError" class="error-banner">
            <span class="error-icon">✕</span>
            {{ generalError }}
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">
                {{ isEditMode ? 'Update Student' : 'Add Student' }}
              </span>
              <span v-else class="loading-animation">
                Loading...
              </span>
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="handleReset"
              :disabled="isLoading"
            >
              {{ isEditMode ? 'Cancel' : 'Clear' }}
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
  name: 'StudentForm',
  props: {
    studentId: {
      type: String,
      default: null
    },
    apiBaseUrl: {
      type: String,
      default: 'http://localhost:8000/api'
    }
  },
  data() {
    return {
      isOpen: false,
      formData: {
        name: '',
        required_hours: '',
        start_date: '',
        end_date: ''
      },
      originalFormData: {},
      errors: {},
      isLoading: false,
      successMessage: '',
      generalError: '',
      isEditMode: false
    };
  },
  computed: {
    isFormValid() {
      return this.formData.name &&
             this.formData.required_hours &&
             this.formData.start_date &&
             this.formData.end_date;
    }
  },
  watch: {
    'formData.start_date'() {
      this.clearErrorForField('start_date');
    },
    'formData.end_date'() {
      this.clearErrorForField('end_date');
    },
    'formData.name'() {
      this.clearErrorForField('name');
    },
    'formData.required_hours'() {
      this.clearErrorForField('required_hours');
    }
  },
  methods: {
    openModal(studentId = null) {
      this.isOpen = true;
      this.isEditMode = !!studentId;
      this.resetForm();
      this.errors = {};

      if (studentId) {
        this.loadStudentData(studentId);
      }
    },

    closeModal() {
      this.isOpen = false;
      this.resetForm();
      this.errors = {};
    },

    async loadStudentData(studentId) {
      this.isLoading = true;
      this.generalError = '';

      try {
        const response = await axios.get(`${this.apiBaseUrl}/students/${studentId}`);
        const student = response.data.data;

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

        this.formData = {
          name: student.name,
          required_hours: student.required_hours,
          start_date: parseDate(student.start_date),
          end_date: parseDate(student.end_date)
        };

        this.originalFormData = { ...this.formData };
      } catch (error) {
        this.generalError = error.response?.data?.message || 'Failed to load student data';
        console.error('Error loading student:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async handleSubmit() {
      this.successMessage = '';
      this.generalError = '';
      this.errors = {};

      if (!this.validateForm()) {
        return;
      }

      this.isLoading = true;

      try {
        let response;

        if (this.isEditMode) {
          response = await axios.put(
            `${this.apiBaseUrl}/students/${this.studentId}`,
            this.formData
          );
        } else {
          response = await axios.post(
            `${this.apiBaseUrl}/students`,
            this.formData
          );
        }

        this.successMessage = response.data.message || 'Student saved successfully!';

        this.$emit('student-saved', response.data.data);

        setTimeout(() => {
          this.successMessage = '';
          if (this.isEditMode) {
            this.closeModal();
          } else {
            this.resetForm();
          }
        }, 1500);
      } catch (error) {
        if (error.response?.status === 422) {
          this.errors = error.response.data.errors || {};
        } else {
          this.generalError = error.response?.data?.message || 'An error occurred while saving the student';
        }
        console.error('Error saving student:', error);
      } finally {
        this.isLoading = false;
      }
    },

    validateForm() {
      const newErrors = {};

      if (!this.formData.name || this.formData.name.trim() === '') {
        newErrors.name = 'Student name is required';
      }

      if (!this.formData.required_hours || this.formData.required_hours <= 0) {
        newErrors.required_hours = 'Required hours must be greater than 0';
      }

      if (!this.formData.start_date) {
        newErrors.start_date = 'Start date is required';
      }

      if (!this.formData.end_date) {
        newErrors.end_date = 'End date is required';
      }

      if (this.formData.start_date && this.formData.end_date) {
        if (new Date(this.formData.end_date) < new Date(this.formData.start_date)) {
          newErrors.end_date = 'End date must be after or equal to start date';
        }
      }

      this.errors = newErrors;
      return Object.keys(newErrors).length === 0;
    },

    handleReset() {
      if (this.isEditMode) {
        this.closeModal();
      } else {
        this.resetForm();
      }
    },

    resetForm() {
      this.formData = {
        name: '',
        required_hours: '',
        start_date: '',
        end_date: ''
      };
      this.errors = {};
      this.successMessage = '';
      this.generalError = '';
    },

    clearErrorForField(field) {
      if (this.errors[field]) {
        delete this.errors[field];
      }
    }
  }
};
</script>

<style scoped>
/* Color Variables - Royal Blue and Orange Theme */
:root {
  --royal-blue: #4169E1;
  --royal-blue-dark: #315AC1;
  --royal-blue-light: #6A8FFF;
  --orange: #FF8C00;
  --orange-dark: #E67E00;
  --orange-light: #FFB84D;
  --white: #FFFFFF;
  --light-gray: #F8F9FA;
  --border-gray: #E0E0E0;
  --text-dark: #1A1A1A;
  --text-light: #666666;
  --error-red: #DC3545;
  --success-green: #28A745;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
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

/* Modal Content */
.modal-content {
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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

/* Modal Header */
.modal-header {
  background: linear-gradient(135deg, #6A8FFF 0%, #5A7FEE 100%);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 2px solid var(--border-gray);
}

.header-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.4;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: var(--white);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-close:hover {
  transform: scale(1.1);
}

/* Modal Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dark);
}

.label-text {
  display: block;
}

.required-asterisk {
  color: var(--orange);
  font-weight: 700;
  font-size: 16px;
}

.form-input {
  padding: 12px 14px;
  border: 2px solid var(--border-gray);
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text-dark);
  background-color: var(--white);
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--royal-blue);
  box-shadow: 0 0 0 3px rgba(65, 105, 225, 0.1);
  background-color: var(--white);
}

.form-input:hover:not(:focus) {
  border-color: var(--royal-blue-light);
}

.form-input.input-error {
  border-color: var(--error-red);
  background-color: rgba(220, 53, 69, 0.02);
}

.form-input.input-error:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.error-message {
  font-size: 12px;
  color: var(--error-red);
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.btn {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-primary {
  background-color: var(--royal-blue);
  color: var(--white);
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--royal-blue-dark);
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.4);
  transform: translateY(-2px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--light-gray);
  color: var(--text-dark);
  border: 2px solid var(--border-gray);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--border-gray);
  border-color: var(--royal-blue);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-animation {
  display: inline-block;
  animation: fade 1s ease-in-out infinite;
}

@keyframes fade {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 1;
  }
}

.success-message {
  background-color: rgba(40, 167, 69, 0.1);
  border: 2px solid var(--success-green);
  color: var(--success-green);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideIn 0.3s ease-out;
}

.success-icon {
  font-size: 16px;
  font-weight: bold;
}

.error-banner {
  background-color: rgba(220, 53, 69, 0.1);
  border: 2px solid var(--error-red);
  color: var(--error-red);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideIn 0.3s ease-out;
}

.error-icon {
  font-size: 16px;
  font-weight: bold;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 480px) {
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-body {
    padding: 16px;
  }

  .header-title h2 {
    font-size: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    padding: 14px 20px;
    font-size: 13px;
  }
}
</style>
