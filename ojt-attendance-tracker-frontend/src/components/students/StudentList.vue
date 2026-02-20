<template>
  <div class="student-list-container">
    <!-- Header Section -->
    <div class="list-header">
      <div class="header-content">
        <h2 class="list-title">Students</h2>
        <p class="list-subtitle">Manage and track student attendance</p>
      </div>
      <div class="header-actions">
        <div class="header-stats">
          <div class="stat-card">
            <span class="stat-label">Total Students</span>
            <span class="stat-value">{{ searchQuery ? `${filteredStudents.length}/${students.length}` : students.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn-add-student" @click="openAddStudentModal">
          + Add Student
      </button>

      <input
          type="text"
          class="search-input"
          placeholder="Search students..."
          v-model="searchQuery"
      />
    </div>
    

    <!-- Student Form Modal -->
    <StudentForm
      ref="studentFormModal"
      :apiBaseUrl="apiBaseUrl"
      @student-saved="onStudentSaved"
    />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading students...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-banner">
      <span class="error-icon">✕</span>
      <div class="error-content">
        <p class="error-title">Failed to Load Students</p>
        <p class="error-message">{{ error }}</p>
      </div>
      <button class="btn-retry" @click="fetchStudents">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="students.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>No Students Yet</h3>
      <p>Create your first student to get started</p>
    </div>

    <!-- No Search Results State -->
    <div v-else-if="filteredStudents.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>No Results Found</h3>
      <p>No students match "{{ searchQuery }}"</p>
      <button class="btn-clear-search" @click="searchQuery = ''">Clear Search</button>
    </div>

    <!-- Students Grid -->
    <div v-else class="students-grid">
      <StudentCard
        v-for="student in filteredStudents"
        :key="student.id"
        :student="student"
        @card-clicked="onStudentCardClicked"
        @delete-clicked="onStudentDeleteClicked"
      />
    </div>

    <!-- Student Details Modal -->
    <StudentDetails
      ref="studentDetailsModal"
      :apiBaseUrl="apiBaseUrl"
    />

    <!-- Confirm Delete Modal -->
    <ConfirmDeleteModal
      ref="confirmDeleteModal"
    />
  </div>
</template>

<script>
import axios from 'axios';
import StudentCard from './StudentCard.vue';
import StudentForm from './StudentForm.vue';
import StudentDetails from './StudentDetails.vue';
import ConfirmDeleteModal from './ConfirmDeleteModal.vue';

export default {
  name: 'StudentList',
  components: {
    StudentCard,
    StudentForm,
    StudentDetails,
    ConfirmDeleteModal
  },
  props: {
    apiBaseUrl: {
      type: String,
      default: 'http://localhost:8000/api'
    },
    autoLoad: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      students: [],
      isLoading: false,
      error: null,
      searchQuery: ''
    };
  },
  computed: {
    filteredStudents() {
      if (!this.searchQuery.trim()) {
        return this.students;
      }

      const query = this.searchQuery.toLowerCase().trim();

      return this.students.filter(student => {
        const nameMatch = student.name && student.name.toLowerCase().includes(query);
        const idMatch = student.id && String(student.id).includes(query);
        return nameMatch || idMatch;
      });
    }
  },
  mounted() {
    if (this.autoLoad) {
      this.fetchStudents();
    }
  },
  methods: {
    async fetchStudents() {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.get(`${this.apiBaseUrl}/students`);
        console.log('API Response:', response.data);
        this.students = response.data.data || [];
        console.log('Students loaded:', this.students);
        this.$emit('students-loaded', this.students);
      } catch (err) {
        this.error =
          err.response?.data?.message ||
          'Failed to load students. Please try again.';
        console.error('Error fetching students:', err);
      } finally {
        this.isLoading = false;
      }
    },
    openAddStudentModal() {
      this.$refs.studentFormModal.openModal();
    },
    onStudentSaved() {
      this.fetchStudents();
    },
    onStudentCardClicked(student) {
      this.$refs.studentDetailsModal.openModal(student);
    },
    async onStudentDeleteClicked(student) {
      const isConfirmed = await this.$refs.confirmDeleteModal.confirm(student.name);
      if (isConfirmed) {
        this.deleteStudent(student);
      }
    },

    deleteStudent(student) {
      axios.delete(`${this.apiBaseUrl}/students/${student.id}`)
        .then(() => {
          this.fetchStudents();
        })
        .catch((err) => {
          alert(
            err.response?.data?.message ||
              'Failed to delete student. Please try again.'
          );
          console.error('Error deleting student:', err);
        });
    }
  }
};
</script>

<style scoped>

.student-list-container {
  width: 100%;
  background-color: var(--light-gray);
  min-height: 100vh;
  padding: 40px 20px;
}

/* Header Section */
.list-header {
  max-width: 1400px;
  margin: 0 auto 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.header-content {
  flex: 1;
  min-width: 200px;
}

.list-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0 0 8px 0;
}

.list-subtitle {
  font-size: 14px;
  color: var(--text-light);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.header-stats {
  display: flex;
  gap: 16px;
}

/* Actions Container */
.actions {
  max-width: 1400px;
  margin: 0 auto 40px;
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* Add Student Button */
.button-container {
  max-width: 1400px;
  margin: 0 auto 40px;
  display: flex;
  justify-content: flex-start;
}

.btn-add-student {
  padding: 10px 20px;
  background-color: var(--royal-blue);
  color: var(--white);
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-add-student:hover {
  background-color: var(--royal-blue-dark);
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
  transform: translateY(-2px);
}

.btn-add-student.btn-active {
  background-color: var(--orange);
}

.btn-add-student.btn-active:hover {
  background-color: var(--orange-dark);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.stat-card {
  background-color: var(--white);
  padding: 16px 24px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 5px solid var(--royal-blue);
  text-align: center;
  min-width: 140px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: var(--text-light);
  font-weight: 600;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--royal-blue);
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
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
  max-width: 1400px;
  margin: 0 auto 40px;
  background-color: rgba(220, 53, 69, 0.1);
  border: 2px solid var(--error-red);
  color: var(--error-red);
  padding: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.error-icon {
  font-size: 24px;
  font-weight: bold;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.error-message {
  font-size: 13px;
  margin: 0;
}

.btn-retry {
  padding: 8px 16px;
  background-color: var(--error-red);
  color: var(--white);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-retry:hover {
  background-color: #c82333;
  transform: translateY(-2px);
}

/* Search Input */
.search-container {
  max-width: 1400px;
  margin: 0 auto 40px;
  width: 100%;
}

.search-input {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
  padding: 12px 16px;
  font-size: 14px;
  border: 2px solid var(--border-gray);
  border-radius: 8px;
  background-color: var(--white);
  color: var(--text-dark);
  transition: all 0.3s ease;
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: var(--royal-blue);
  box-shadow: 0 0 0 3px rgba(65, 105, 225, 0.1);
}

.search-input::placeholder {
  color: var(--text-light);
}

/* Clear Search Button */
.btn-clear-search {
  padding: 10px 20px;
  background-color: var(--royal-blue);
  color: var(--white);
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 20px;
}

.btn-clear-search:hover {
  background-color: var(--royal-blue-dark);
  box-shadow: 0 4px 12px rgba(65, 105, 225, 0.3);
  transform: translateY(-2px);
}

/* Empty State */
.empty-state {
  max-width: 600px;
  margin: 0 auto;
  background-color: var(--white);
  border-radius: 12px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0 0 12px 0;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-light);
  margin: 0;
}

/* Students Grid */
.students-grid {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 1200px) {
  .students-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .student-list-container {
    padding: 24px 16px;
  }

  .list-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 30px;
  }

  .header-stats {
    width: 100%;
  }

  .list-title {
    font-size: 28px;
  }

  .actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .btn-add-student {
    width: 100%;
  }

  .search-input {
    width: 100%;
    max-width: 100%;
  }

  .students-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .student-list-container {
    padding: 16px;
  }

  .list-title {
    font-size: 24px;
  }

  .actions {
    gap: 10px;
  }

  .btn-add-student {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .search-input {
    padding: 8px 10px;
    font-size: 0.9rem;
  }

  .students-grid {
    grid-template-columns: 1fr;
  }

  .header-stats {
    width: 100%;
  }

  .stat-card {
    flex: 1;
  }
}
</style>
