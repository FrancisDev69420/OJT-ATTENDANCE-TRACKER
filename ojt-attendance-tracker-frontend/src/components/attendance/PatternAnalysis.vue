<template>
  <div>
    <!-- Pattern Analysis Button -->
    <button class="btn-pattern-analysis" @click="openModal(studentId, studentName)" title="View attendance pattern analysis">
      📊 Pattern Analysis
    </button>

    <!-- Pattern Analysis Modal -->
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <div class="header-title">
            <h2>Attendance Pattern Analysis</h2>
            <p class="student-name-subtitle">{{ currentStudentName }}</p>
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
            <p>Analyzing attendance patterns...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="error-banner">
            <span class="error-icon">✕</span>
            <div class="error-content">
              <p class="error-title">Analysis Failed</p>
              <p class="error-message">{{ error }}</p>
            </div>
          </div>

          <!-- Content -->
          <div v-else-if="analysisData">
            <!-- Risk Classification Card -->
            <div class="analysis-section">
              <h4 class="section-title">Risk Classification</h4>
              <div class="risk-card" :class="`risk-${analysisData.risk_classification}`">
                <div class="risk-icon">
                  {{ getRiskIcon(analysisData.risk_classification) }}
                </div>
                <div class="risk-info">
                  <p class="risk-label">Current Status</p>
                  <p class="risk-value">{{ formatRiskLevel(analysisData.risk_classification) }}</p>
                </div>
              </div>
            </div>

            <!-- Attendance Summary -->
            <div class="analysis-section">
              <h4 class="section-title">Attendance Summary</h4>
              <div class="summary-grid">
                <div class="summary-item">
                  <div class="summary-label">Total Days</div>
                  <div class="summary-stat">{{ analysisData.summary.total_days }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Present</div>
                  <div class="summary-stat present">{{ analysisData.summary.present_count }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Late</div>
                  <div class="summary-stat late">{{ analysisData.summary.late_count }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Absent</div>
                  <div class="summary-stat absent">{{ analysisData.summary.absent_count }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Half Day</div>
                  <div class="summary-stat half-day">{{ analysisData.summary.half_day_count }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Holiday</div>
                  <div class="summary-stat holiday">{{ analysisData.summary.holiday_count }}</div>
                </div>
              </div>
            </div>

            <!-- Attendance Rate -->
            <div class="analysis-section">
              <h4 class="section-title">Attendance Rate</h4>
              <div class="rate-card">
                <div class="rate-circle" :style="{ '--percentage': analysisData.summary.attendance_rate }">
                  <div class="rate-value">{{ analysisData.summary.attendance_rate }}%</div>
                </div>
                <div class="rate-info">
                  <p class="rate-pattern">Pattern: <span class="pattern-badge">{{ formatPattern(analysisData.summary.pattern) }}</span></p>
                </div>
              </div>
            </div>

            <!-- Hours Information -->
            <div class="analysis-section">
              <h4 class="section-title">Hours Completion</h4>
              <div class="hours-grid">
                <div class="hours-item">
                  <label class="hours-label">Required Hours</label>
                  <div class="hours-value">{{ analysisData.hours.required_hours }} hrs</div>
                </div>
                <div class="hours-item">
                  <label class="hours-label">Hours Rendered</label>
                  <div class="hours-value completed">{{ analysisData.hours.hours_rendered }} hrs</div>
                </div>
                <div class="hours-item">
                  <label class="hours-label">Remaining Hours</label>
                  <div class="hours-value remaining">{{ analysisData.hours.remaining_hours }} hrs</div>
                </div>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: analysisData.hours.hours_completion_percentage + '%' }"></div>
                </div>
                <p class="progress-text">{{ analysisData.hours.hours_completion_percentage }}% Complete</p>
              </div>
            </div>

            <!-- Trend Analysis -->
            <div class="analysis-section">
              <h4 class="section-title">Trend Analysis</h4>
              <div class="trend-container">
                <div v-if="analysisData.trend.trend !== 'insufficient_data'" class="trend-card">
                  <div class="trend-header">
                    <span class="trend-direction" :class="`trend-${analysisData.trend.trend}`">
                      {{ getTrendIcon(analysisData.trend.trend) }}
                      {{ formatTrend(analysisData.trend.trend) }}
                    </span>
                  </div>
                  <div class="trend-stats">
                    <div class="trend-stat">
                      <label>First Half</label>
                      <span>{{ analysisData.trend.first_half_rate }}%</span>
                    </div>
                    <div class="trend-divider"></div>
                    <div class="trend-stat">
                      <label>Second Half</label>
                      <span>{{ analysisData.trend.second_half_rate }}%</span>
                    </div>
                    <div class="trend-divider"></div>
                    <div class="trend-stat">
                      <label>Change</label>
                      <span :class="{ 'positive': analysisData.trend.change_percentage > 0, 'negative': analysisData.trend.change_percentage < 0 }">
                        {{ analysisData.trend.change_percentage > 0 ? '+' : '' }}{{ analysisData.trend.change_percentage }}%
                      </span>
                    </div>
                  </div>
                </div>
                <div v-else class="trend-card no-data">
                  <p>Insufficient data for trend analysis (requires at least 4 records)</p>
                </div>
              </div>
            </div>

            <!-- Recommendations -->
            <div class="analysis-section">
              <h4 class="section-title">Recommendations</h4>
              <div class="recommendations-list">
                <div v-for="(rec, index) in analysisData.recommendations" :key="index" class="recommendation-item">
                  <span class="recommendation-icon">💡</span>
                  <p class="recommendation-text">{{ rec }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Close</button>
          <button class="btn-primary" @click="refreshAnalysis" :disabled="isLoading">
            {{ isLoading ? 'Refreshing...' : 'Refresh Analysis' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PatternAnalysis',
  props: {
    studentId: {
      type: String,
      required: false,
      default: null
    },
    studentName: {
      type: String,
      required: false,
      default: 'Student'
    },
    apiBaseUrl: {
      type: String,
      default: 'http://localhost:8001'
    }
  },
  data() {
    return {
      isOpen: false,
      isLoading: false,
      error: null,
      analysisData: null,
      currentStudentName: 'Student'
    };
  },
  methods: {
    openModal(studentId = null, studentName = null) {
      const id = studentId || this.studentId;
      const name = studentName || this.studentName;

      if (!id) {
        this.error = 'Student ID is required';
        return;
      }

      this.isOpen = true;
      this.error = null;
      this.analysisData = null;
      this.currentStudentName = name;
      this.fetchAnalysis(id);
    },

    closeModal() {
      this.isOpen = false;
      this.analysisData = null;
      this.error = null;
    },

    async fetchAnalysis(studentId) {
      try {
        this.isLoading = true;
        this.error = null;

        const response = await axios.get(
          `${this.apiBaseUrl}/api/students/${studentId}/analysis`
        );

        if (response.data) {
          this.analysisData = response.data;
        }
      } catch (err) {
        if (err.response?.status === 404) {
          this.error = err.response?.data?.detail || 'Student not found or insufficient attendance data';
        } else {
          this.error = err.response?.data?.detail || 'Failed to load analysis. Please try again.';
        }
        console.error('Error fetching analysis:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async refreshAnalysis() {
      if (this.analysisData) {
        await this.fetchAnalysis(this.analysisData.student_id);
      }
    },

    getRiskIcon(riskLevel) {
      const icons = {
        excellent: '✅',
        good: '👍',
        warning: '⚠️',
        critical: '🚨',
        insufficient_data: '❓'
      };
      return icons[riskLevel] || '❓';
    },

    formatRiskLevel(level) {
      const labels = {
        excellent: 'Excellent',
        good: 'Good',
        warning: 'Warning',
        critical: 'Critical',
        insufficient_data: 'Insufficient Data'
      };
      return labels[level] || level;
    },

    formatPattern(pattern) {
      if (!pattern) return 'N/A';
      return pattern
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },

    getTrendIcon(trend) {
      const icons = {
        improving: '📈',
        declining: '📉',
        stable: '➡️'
      };
      return icons[trend] || '❓';
    },

    formatTrend(trend) {
      const labels = {
        improving: 'Improving',
        declining: 'Declining',
        stable: 'Stable'
      };
      return labels[trend] || trend;
    }
  }
};
</script>

<style scoped>
/* Button */
.btn-pattern-analysis {
  padding: 8px 16px;
  background-color: #4169e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-pattern-analysis:hover {
  background-color: #3051c3;
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.3);
}

.btn-pattern-analysis:active {
  transform: translateY(1px);
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
  z-index: 1100;
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
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 800px;
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
  background: linear-gradient(135deg, #4169e1 0%, #3051c3 100%);
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #e0e8ff;
}

.header-title {
  flex: 1;
}

.header-title h2 {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0 0 4px 0;
}

.student-name-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: white;
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

/* Analysis Sections */
.analysis-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e8ff;
}

/* Risk Card */
.risk-card {
  padding: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 2px solid;
  background-color: #f8f9ff;
}

.risk-card.risk-excellent {
  border-color: #28a745;
  background-color: rgba(40, 167, 69, 0.1);
}

.risk-card.risk-good {
  border-color: #4169e1;
  background-color: rgba(65, 105, 225, 0.1);
}

.risk-card.risk-warning {
  border-color: #ffc107;
  background-color: rgba(255, 193, 7, 0.1);
}

.risk-card.risk-critical {
  border-color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.risk-icon {
  font-size: 40px;
  flex-shrink: 0;
}

.risk-info {
  flex: 1;
}

.risk-label {
  font-size: 12px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  margin: 0 0 8px 0;
  letter-spacing: 0.3px;
}

.risk-value {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: #333;
}

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.summary-item {
  background-color: #f5f7ff;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #4169e1;
  text-align: center;
}

.summary-label {
  font-size: 11px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}

.summary-stat {
  font-size: 24px;
  font-weight: 700;
  color: #4169e1;
}

.summary-stat.present {
  color: #28a745;
}

.summary-stat.late {
  color: #ffc107;
}

.summary-stat.absent {
  color: #dc3545;
}

.summary-stat.half-day {
  color: #17a2b8;
}

.summary-stat.holiday {
  color: #6c757d;
}

/* Rate Card */
.rate-card {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 20px;
  background-color: #f5f7ff;
  border-radius: 10px;
}

.rate-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(#4169e1 0deg calc(var(--percentage) * 3.6deg), #e0e8ff calc(var(--percentage) * 3.6deg) 360deg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
}

.rate-circle::before {
  content: '';
  position: absolute;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: white;
}

.rate-value {
  font-size: 24px;
  font-weight: 700;
  color: #4169e1;
  position: relative;
  z-index: 1;
}

.rate-info {
  flex: 1;
}

.rate-pattern {
  font-size: 14px;
  color: #333;
  margin: 0;
}

.pattern-badge {
  display: inline-block;
  padding: 6px 12px;
  background-color: #4169e1;
  color: white;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
}

/* Hours Grid */
.hours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.hours-item {
  background-color: #f5f7ff;
  padding: 16px;
  border-radius: 8px;
  border-bottom: 3px solid #4169e1;
}

.hours-label {
  display: block;
  font-size: 11px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}

.hours-value {
  font-size: 20px;
  font-weight: 700;
  color: #4169e1;
}

.hours-value.completed {
  color: #28a745;
}

.hours-value.remaining {
  color: #ffc107;
}

/* Progress Bar */
.progress-bar-container {
  background-color: #f5f7ff;
  padding: 16px;
  border-radius: 8px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background-color: #e0e8ff;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4169e1 0%, #6a8fff 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #999;
  font-weight: 600;
  margin: 0;
}

/* Trend Container */
.trend-container {
  margin-top: 12px;
}

.trend-card {
  background-color: #f5f7ff;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #4169e1;
}

.trend-card.no-data {
  padding: 32px 20px;
  text-align: center;
  color: #999;
  border-left-color: #e0e8ff;
}

.trend-header {
  margin-bottom: 16px;
}

.trend-direction {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
}

.trend-direction.trend-improving {
  background-color: rgba(40, 167, 69, 0.2);
  color: #28a745;
}

.trend-direction.trend-declining {
  background-color: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.trend-direction.trend-stable {
  background-color: rgba(65, 105, 225, 0.2);
  color: #4169e1;
}

.trend-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.trend-stat {
  flex: 1;
  text-align: center;
}

.trend-stat label {
  display: block;
  font-size: 11px;
  color: #999;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 6px;
  letter-spacing: 0.3px;
}

.trend-stat span {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #4169e1;
}

.trend-stat span.positive {
  color: #28a745;
}

.trend-stat span.negative {
  color: #dc3545;
}

.trend-divider {
  width: 2px;
  height: 40px;
  background-color: #e0e8ff;
  flex-shrink: 0;
}

/* Recommendations List */
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #f5f7ff;
  border-radius: 8px;
  border-left: 4px solid #ffc107;
  align-items: flex-start;
}

.recommendation-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.recommendation-text {
  font-size: 13px;
  color: #333;
  margin: 0;
  line-height: 1.5;
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
  border: 5px solid #e0e8ff;
  border-top: 5px solid #4169e1;
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
  color: #999;
  font-weight: 500;
}

/* Error State */
.error-banner {
  background-color: rgba(220, 53, 69, 0.1);
  border: 2px solid #dc3545;
  color: #dc3545;
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
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 2px 0;
}

.error-message {
  font-size: 16px;
  margin: 0;
}

/* Modal Footer */
.modal-footer {
  padding: 16px 24px;
  background-color: #f5f7ff;
  border-top: 1px solid #e0e8ff;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-primary {
  padding: 10px 20px;
  background-color: #4169e1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3051c3;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: #999;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: #777;
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

  .header-title h2 {
    font-size: 20px;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .rate-card {
    flex-direction: column;
    gap: 16px;
  }

  .trend-stats {
    flex-direction: column;
    gap: 16px;
  }

  .trend-divider {
    display: none;
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

  .modal-body {
    padding: 12px;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .summary-item {
    padding: 12px;
  }

  .summary-stat {
    font-size: 18px;
  }

  .hours-grid {
    grid-template-columns: 1fr;
  }

  .recommendation-item {
    padding: 12px;
  }
}
</style>
