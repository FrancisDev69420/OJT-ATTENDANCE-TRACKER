<template>
  <div class="home-container">
   

    <!-- Main Content -->
    <main class="main-content">
      <!-- Welcome Section -->
      <section class="welcome-section">
        <div class="welcome-content">
          <h2 class="welcome-title">Welcome to OJT Attendance Tracker</h2>
          <p class="welcome-subtitle">
            A comprehensive system to manage and track student attendance during
            their on-the-job training period
          </p>
        </div>
      </section>

      <!-- Student List Section -->
      <section class="students-section" id="students">
        <StudentList
          ref="studentList"
          :apiBaseUrl="apiBaseUrl"
          @students-loaded="onStudentsLoaded"
        />
      </section>
    </main>
  </div>
</template>

<script>
import StudentList from './students/StudentList.vue';
import StudentForm from './students/StudentForm.vue';

export default {
  name: 'Home',
  components: {
    StudentList,
    StudentForm
  },
  data() {
    return {
      apiBaseUrl: 'http://localhost:8000/api',
      showStudentForm: false
    };
  },
  methods: {
    onStudentsLoaded(students) {
      console.log('Students loaded:', students);
    }
  }
};
</script>

<style scoped>

.home-container {
  width: 100%;
  background-color: var(--light-gray);
  min-height: 100vh;
}

/* Header Styles */
.app-header {
  background-color: var(--white);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 4px solid var(--orange);
}

.header-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  flex: 1;
}

.app-logo {
  font-size: 24px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0;
  letter-spacing: -0.5px;
}

/* Main Content */
.main-content {
  width: 100%;
}

/* Welcome Section */
.welcome-section {
  background-color: #F8F9FA;
  padding-top: 40px;
  text-align: center;
}

.welcome-content {
  max-width: 800px;
  margin: 0 auto;
}

.welcome-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--royal-blue);
  margin-bottom: 16px;
}

.welcome-subtitle {
  font-size: 16px;
  color: var(--text-light);
  line-height: 1.6;
  margin: 0;
}

/* Form Section */
.form-section {
  width: 100%;
  background-color: var(--white);
  padding: 40px 20px;
  border-bottom: 2px solid var(--border-gray);
}

.form-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background-color: var(--light-gray);
  color: var(--text-dark);
  font-size: 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: var(--orange);
  color: var(--white);
}

/* Students Section */
.students-section {
  width: 100%;
  padding: 20px;
}

.section-header {
  max-width: 1200px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--royal-blue);
  margin: 0;
}


/* Responsive Design */
@media (max-width: 768px) {
  .header-wrapper {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .app-logo {
    font-size: 20px;
  }

  .welcome-title {
    font-size: 28px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .welcome-section {
    padding: 40px 20px;
  }
}

@media (max-width: 480px) {
  .header-wrapper {
    padding: 12px 16px;
  }

  .app-logo {
    font-size: 18px;
  }

  .welcome-title {
    font-size: 24px;
  }

  .welcome-subtitle {
    font-size: 13px;
  }

  .welcome-section {
    padding: 30px 16px;
  }
}
</style>