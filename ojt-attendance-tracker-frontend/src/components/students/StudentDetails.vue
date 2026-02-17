<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-title">
          <h2>Student Details</h2>
        </div>
        <button class="btn-close" @click="closeModal" aria-label="Close modal">
          ✕
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <div class="spinner"></div>
          <p>Loading student details...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-banner">
          <span class="error-icon">✕</span>
          <div class="error-content">
            <p class="error-title">Failed to Load Details</p>
            <p class="error-message">{{ error }}</p>
          </div>
        </div>

        <!-- Content -->
        <div v-else-if="studentData">
          <!-- Student Header -->
          <div class="student-header">
            <div class="student-avatar" @click="openEditStudentModal" style="cursor: pointer;" title="Click to edit student">
              {{ getInitials(studentData?.name) }}
            </div>
            <div class="student-info">
              <h3 class="student-name">{{ studentData?.name || 'N/A' }}</h3>
              <p class="student-id">ID: {{ studentData?.id?.substring(0, 8) }}</p>
            </div>

            <div class="button-group">
                <PatternAnalysis
                    ref="patternAnalysis"
                    :studentId="studentId"
                    :studentName="studentData?.name"
                    :apiBaseUrl="apiAnalysisUrl"
                />
                <button class="btn-record-attendance" @click="openAttendanceForm">
                    + Record Attendance
                </button>
            </div>
          </div>

          <!-- Student Basic Info -->
          <div class="info-section">
            <h4 class="section-title">Basic Information</h4>
            <div class="info-grid">
              <div class="info-item">
                <label class="info-label">Required Hours</label>
                <div class="info-value hours-badge">
                  {{ studentData?.required_hours || 0 }} hours
                </div>
              </div>
              <div class="info-item">
                <label class="info-label">Start Date</label>
                <div class="info-value">
                  {{ formatDate(studentData?.start_date) }}
                </div>
              </div>
              <div class="info-item">
                <label class="info-label">End Date</label>
                <div class="info-value">
                  {{ formatDate(studentData?.end_date) }}
                </div>
              </div>
              <div class="info-item">
                <label class="info-label">Created</label>
                <div class="info-value">
                  {{ formatDateTime(studentData?.created_at) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Attendance Summary Section -->
          <div class="info-section">
            <h4 class="section-title">Attendance Summary</h4>
            <div v-if="attendanceSummary" class="summary-grid">
              <div class="summary-card">
                <div class="summary-icon total">📊</div>
                <div class="summary-info">
                  <p class="summary-label">Total Hours Rendered</p>
                  <p class="summary-value">{{ attendanceSummary.total_hours_rendered }} hours</p>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-icon remaining">⏱️</div>
                <div class="summary-info">
                  <p class="summary-label">Remaining Hours</p>
                  <p class="summary-value" :class="{ 'text-warning': attendanceSummary.remaining_hours > 0, 'text-success': attendanceSummary.remaining_hours === 0 }">
                    {{ attendanceSummary.remaining_hours }} hours
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="loading-summary">
              <p>Loading attendance data...</p>
            </div>
          </div>

          <!-- Attendance Records -->
          <div class="info-section">
            <div class="attendance-header">
              <h4 class="section-title">Attendance Records</h4>
            </div>
            <div v-if="attendanceRecords && attendanceRecords.length > 0" class="attendance-table-wrapper">
              <div class="attendance-table-header">
                <div class="header-cell date">Date</div>
                <div class="header-cell time">Time</div>
                <div class="header-cell status">Status</div>
                <div class="header-cell hours">Hours</div>
              </div>
              <div class="attendance-list">
                <div v-for="record in attendanceRecords" :key="record.id" class="attendance-item">
                  <div class="attendance-date">
                    {{ formatDate(record.date) }}
                  </div>
                  <div class="attendance-time">
                    {{ formatTime(record.time_in) }} - {{ formatTime(record.time_out) }}
                  </div>
                  <div class="attendance-status" :class="record.status">
                    {{ capitalizeStatus(record.status) }}
                  </div>
                  <div class="attendance-hours">
                    {{ record.hours_rendered }} hrs
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-attendance">
              <p>No attendance records found</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button class="btn-secondary" @click="closeModal">Close</button>
      </div>
    </div>
  </div>

  <!-- Attendance Form Modal -->
  <AttendanceForm
    ref="attendanceForm"
    :apiBaseUrl="apiBaseUrl"
    @attendance-saved="onAttendanceSaved"
  />

  <!-- Student Form Modal -->
  <StudentForm
    ref="studentForm"
    :studentId="studentId"
    :apiBaseUrl="apiBaseUrl"
    @student-saved="onStudentFormSaved"
  />
</template>

<script>
import axios from 'axios';
import AttendanceForm from '../attendance/AttendanceForm.vue';
import PatternAnalysis from '../attendance/PatternAnalysis.vue';
import StudentForm from './StudentForm.vue';

export default {
  name: 'StudentDetails',
  components: {
    AttendanceForm,
    PatternAnalysis,
    StudentForm,
  },
  props: {
    apiBaseUrl: {
      type: String,
      default: 'http://localhost:8000/api'
    },
    apiAnalysisUrl: {
      type: String,
      default: 'http://localhost:8001'
    }
  },
  data() {
    return {
      isOpen: false,
      isLoading: false,
      error: null,
      studentData: null,
      attendanceSummary: null,
      attendanceRecords: []
    };
  },
  computed: {
    studentId() {
      return this.studentData?.id;
    }
  },
  methods: {
    openModal(student) {
      this.isOpen = true;
      this.studentData = student;
      this.error = null;
      this.attendanceSummary = null;
      this.attendanceRecords = [];
      this.isLoading = true;
      
      // Debug: log the full student object received
      console.log('Student object received:', student);
      console.log('Student ID:', student.id, 'ID type:', typeof student.id, 'ID length:', student.id ? student.id.length : 0);
      
      // Fetch attendance summary and records
      this.fetchStudentData(student.id);
    },

    closeModal() {
      this.isOpen = false;
      this.studentData = null;
      this.attendanceSummary = null;
      this.attendanceRecords = [];
      this.error = null;
    },

    openAttendanceForm() {
      this.$refs.attendanceForm.openModal(this.studentId);
    },

    openEditStudentModal() {
      this.$refs.studentForm.openModal(this.studentId);
    },

    async onAttendanceSaved(attendanceRecord) {
      // Refresh the attendance records when a new one is added
      console.log('Attendance saved:', attendanceRecord);
      this.fetchStudentData(this.studentId);
    },

    async onStudentFormSaved(updatedStudent) {
      // Refresh student data when student is updated
      console.log('Student updated:', updatedStudent);
      this.fetchStudentData(this.studentId);
    },

    async fetchStudentData(studentId) {
      try {
        this.isLoading = true;
        this.error = null;

        // Debug: log the student ID being used
        console.log('Fetching student data with ID:', studentId, 'ID length:', studentId ? studentId.length : 0);

        // Fetch remaining hours and attendance records in parallel
        const [remainingHoursRes, attendancesRes] = await Promise.all([
          axios.get(`${this.apiBaseUrl}/students/${studentId}/remaining-hours`),
          axios.get(`${this.apiBaseUrl}/students/${studentId}/attendances`)
        ]);

        if (remainingHoursRes.data?.data) {
          this.attendanceSummary = remainingHoursRes.data.data;
        }

        if (attendancesRes.data?.data) {
          // Sort by date descending
          this.attendanceRecords = attendancesRes.data.data.sort((a, b) => {
            return new Date(b.date) - new Date(a.date);
          });
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load student details. Please try again.';
        console.error('Error fetching student data:', err);
      } finally {
        this.isLoading = false;
      }
    },

    getInitials(name) {
      if (!name) return '?';
      try {
        return String(name)
          .split(' ')
          .map((word) => word.charAt(0))
          .join('')
          .toUpperCase()
          .substring(0, 2);
      } catch (e) {
        console.error('Error getting initials:', e);
        return '?';
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        console.error('Error formatting date:', e);
        return 'N/A';
      }
    },

    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      } catch (e) {
        console.error('Error formatting date time:', e);
        return 'N/A';
      }
    },

    formatTime(timeString) {
      if (!timeString) return 'N/A';
      try {
        // Time is already in H:i format from the API
        return timeString;
      } catch (e) {
        console.error('Error formatting time:', e);
        return 'N/A';
      }
    },

    capitalizeStatus(status) {
      if (!status) return 'N/A';
      return String(status)
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
  }
};
</script>

<style scoped>
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

/* Modal Content */
.modal-content {
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 700px;
  width: 90%;
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
  align-items: center;
  border-bottom: 2px solid var(--border-gray);
}

.header-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--white);
  margin: 0;
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

/* Student Header */
.student-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid var(--light-gray);
}

.student-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6A8FFF 0%, #5A7FEE 100%);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.student-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(65, 105, 225, 0.4);
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0 0 4px 0;
}

.student-id {
  font-size: 12px;
  color: var(--text-light);
  margin: 0;
  font-weight: 500;
}

/* Info Sections */
.info-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-dark);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--light-gray);
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.info-item {
  background-color: var(--light-gray);
  padding: 16px;
  border-radius: 8px;
}

.info-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}

.info-value {
  font-size: 14px;
  color: var(--royal-blue);
  font-weight: 600;
}

.hours-badge {
  background-color: var(--orange);
  color: var(--white);
  padding: 8px 12px;
  border-radius: 6px;
  display: inline-block;
}

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-card {
  background: linear-gradient(135deg, #f5f7ff 0%, #f0f4ff 100%);
  border: 2px solid #e0e8ff;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.summary-card:hover {
  border-color: var(--royal-blue);
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.1);
}

.summary-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.summary-info {
  flex: 1;
}

.summary-label {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 600;
  text-transform: uppercase;
  margin: 0 0 6px 0;
  letter-spacing: 0.3px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0;
}

.summary-value.text-warning {
  color: var(--orange);
}

.summary-value.text-success {
  color: #28a745;
}

/* Attendance Header with Button */
.attendance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.button-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-record-attendance {
  padding: 8px 16px;
  background-color: #ff8c42;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-record-attendance:hover {
  background-color: #e67e2f;
  box-shadow: 0 2px 8px rgba(255, 140, 42, 0.3);
}

.btn-record-attendance:active {
  transform: translateY(1px);
}

/* Attendance Table */
.attendance-table-wrapper {
  border: 1px solid var(--border-gray);
  border-radius: 8px;
  overflow: hidden;
}

.attendance-table-header {
  display: grid;
  grid-template-columns: 120px 140px 100px 80px;
  gap: 12px;
  padding: 12px;
  padding-left: 12px;
  background-color: #f0f4ff;
  border-bottom: 2px solid var(--border-gray);
  font-weight: 600;
  color: var(--royal-blue);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.header-cell {
  display: flex;
  align-items: center;
}

.hours{
    margin-left: 30px ;
}

/* Attendance List */
.attendance-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.attendance-item {
  display: grid;
  grid-template-columns: 120px 140px 100px 80px;
  gap: 12px;
  padding: 12px;
  background-color: var(--white);
  border-bottom: 1px solid var(--light-gray);
  align-items: center;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.attendance-item:last-child {
  border-bottom: none;
}

.attendance-item:hover {
  background-color: #fafbff;
}

.attendance-date {
  font-weight: 600;
  color: var(--text-dark);
}

.attendance-time {
  font-size: 11px;
  color: var(--text-light);
}

.attendance-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  text-align: center;
  text-transform: capitalize;
}

.attendance-status.present {
  background-color: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.attendance-status.absent {
  background-color: rgba(220, 53, 69, 0.2);
  color: var(--error-red);
}

.attendance-status.late {
  background-color: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.attendance-status.half_day {
  background-color: rgba(23, 162, 184, 0.2);
  color: #17a2b8;
}

.attendance-status.holiday {
  background-color: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.attendance-hours {
  font-weight: 600;
  color: var(--royal-blue);
  text-align: right;
}

.empty-attendance {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-light);
  background-color: var(--light-gray);
  border-radius: 8px;
  font-size: 14px;
}

.loading-summary {
  padding: 32px 16px;
  text-align: center;
  color: var(--text-light);
  font-size: 14px;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid var(--border-gray);
  border-top: 5px solid var(--royal-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-container p {
  font-size: 14px;
  color: var(--text-light);
  font-weight: 500;
}

/* Error State */
.error-banner {
  background-color: rgba(220, 53, 69, 0.1);
  border: 2px solid var(--error-red);
  color: var(--error-red);
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 2px 0;
}

.error-message {
  font-size: 12px;
  margin: 0;
}

/* Modal Footer */
.modal-footer {
  padding: 16px 24px;
  background-color: var(--light-gray);
  border-top: 1px solid var(--border-gray);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: var(--text-light);
  color: var(--white);
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: var(--text-dark);
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 768px) {
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

  .modal-footer {
    padding: 12px 16px;
  }

  .student-header {
    margin-bottom: 24px;
  }

  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .attendance-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .attendance-hours {
    text-align: left;
  }

  .header-title h2 {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .modal-content {
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .modal-header {
    padding: 12px 16px;
  }

  .header-title h2 {
    font-size: 18px;
  }

  .btn-close {
    font-size: 24px;
  }

  .student-avatar {
    width: 60px;
    height: 60px;
    font-size: 20px;
  }

  .student-name {
    font-size: 18px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .attendance-item {
    font-size: 11px;
  }
}
</style>
