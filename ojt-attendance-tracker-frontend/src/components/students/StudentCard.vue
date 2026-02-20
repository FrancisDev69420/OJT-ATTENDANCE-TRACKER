<template>
  <div class="student-card" @click="onCardClick">
    <!-- Card Header -->
    <div class="card-header">

      <div class="student-avatar">
        {{ getInitials(student?.name) }}
      </div>

      <div class="header-info">
        <h3 class="student-name">{{ student?.name || 'N/A' }}</h3>
        <p class="student-id">ID: {{ student?.id?.substring(0, 8) || 'N/A' }}</p>
      </div>

      <div class="delete-button">
        <button @click.stop="onDeleteClick" class="delete-btn">
          <TrashIcon class="icon" />
        </button>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <!-- Required Hours -->
      <div class="info-row">
        <div class="info-label">
          <span class="label-icon">⏱️</span>
          <span>Required Hours</span>
        </div>
        <div class="info-value hours-badge">
          {{ student?.required_hours || 0 }}
        </div>
      </div>

      <!-- Start Date -->
      <div class="info-row">
        <div class="info-label">
          <span class="label-icon">📅</span>
          <span>Start Date</span>
        </div>
        <div class="info-value">
          {{ formatDate(student?.start_date) }}
        </div>
      </div>

      <!-- End Date -->
      <div class="info-row">
        <div class="info-label">
          <span class="label-icon">📆</span>
          <span>End Date</span>
        </div>
        <div class="info-value">
          {{ formatDate(student?.end_date) }}
        </div>
      </div>
    </div>

    <!-- Card Footer -->
    <div class="card-footer">
      <div class="created-info">
        <small v-if="student?.created_at">Created: {{ formatDateTime(student.created_at) }}</small>
        <small v-else>Created: N/A</small>
      </div>
    </div>
  </div>
</template>

<script>
import { TrashIcon } from '@heroicons/vue/24/solid'

export default {
  name: 'StudentCard',
  components: {
    TrashIcon
  },
  props: {
    student: {
      type: Object,
      required: true
    }
  },
  methods: {
    onCardClick() {
      this.$emit('card-clicked', this.student);
    },
    onDeleteClick() {
      this.$emit('delete-clicked', this.student);
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
        console.error('Error getting initials:', e, 'name:', name);
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
    }
  }
};
</script>

<style scoped>

.student-card {
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
}

.student-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
  border-left-color: var(--orange);
}

/* Card Header */
.card-header {
  background-color: rgb(71, 71, 173);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 2px solid var(--border-gray);
}

.delete-btn {
  background: transparent;
  border: none;
  cursor: pointer;
}


.icon {
  width: 20px;
  height: 20px;
  color: #fd1414;
  transition: all 0.2s ease;
}

.delete-btn:hover .icon {
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
}

.student-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--royal-blue);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--white);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-id {
  font-size: 14px;
  color:var(--white);
  margin: 4px 0 0 0;
}

/* Card Body */
.card-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background-color: var(--light-gray);
  border-radius: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dark);
}

.label-icon {
  font-size: 16px;
}

.info-value {
  font-size: 14px;
  color: var(--royal-blue);
  font-weight: 600;
}

.hours-badge {
  background-color: var(--orange);
  color: var(--white);
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 700;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px;
  background-color: var(--light-gray);
  border-top: 1px solid var(--border-gray);
}

.created-info {
  font-size: 11px;
  color: var(--text-light);
  text-align: right;
}

/* Responsive Design */
@media (max-width: 480px) {
  .card-header {
    padding: 16px;
  }

  .card-body {
    padding: 16px;
    gap: 12px;
  }

  .student-name {
    font-size: 15px;
  }

  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
