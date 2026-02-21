<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>Delete Attendance Record</h3>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <div class="warning-icon">⚠️</div>
        <h4>Are you sure?</h4>
        <p class="warning-text">
          This will permanently delete the attendance record for <strong>{{ recordDate }}</strong>.
          This action cannot be undone.
        </p>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button 
          class="btn-cancel" 
          @click="closeModal"
          :disabled="isDeleting"
        >
          Cancel
        </button>
        <button 
          class="btn-delete" 
          @click="confirmDelete"
          :disabled="isDeleting"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete Record' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeleteConfirmationModal',
  data() {
    return {
      isOpen: false,
      recordId: null,
      recordDate: null,
      isDeleting: false
    };
  },
  methods: {
    openModal(recordId, recordDate) {
      this.isOpen = true;
      this.recordId = recordId;
      this.recordDate = recordDate;
      this.isDeleting = false;
    },
    closeModal() {
      this.isOpen = false;
      this.recordId = null;
      this.recordDate = null;
      this.isDeleting = false;
    },
    async confirmDelete() {
      this.$emit('delete-confirmed', this.recordId);
      // Close modal after emitting event
      this.closeModal();
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
  z-index: 2000;
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
  max-width: 400px;
  width: 90%;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

/* Modal Body */
.modal-body {
  padding: 32px 24px;
  text-align: center;
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-body h4 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.warning-text {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.warning-text strong {
  color: #d32f2f;
  font-weight: 600;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
}

.btn-cancel,
.btn-delete {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background-color: #f5f5f5;
  color: #333;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-delete {
  background-color: #d32f2f;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #b71c1c;
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
}

.btn-cancel:disabled,
.btn-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-delete:active:not(:disabled) {
  transform: translateY(1px);
}

/* Responsive Design */
@media (max-width: 480px) {
  .modal-content {
    width: 95%;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-body {
    padding: 24px 20px;
  }

  .modal-footer {
    padding: 16px 20px;
    flex-direction: column;
  }

  .btn-cancel,
  .btn-delete {
    width: 100%;
  }

  .warning-icon {
    font-size: 40px;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  .modal-body h4 {
    font-size: 16px;
  }

  .warning-text {
    font-size: 13px;
  }
}
</style>
