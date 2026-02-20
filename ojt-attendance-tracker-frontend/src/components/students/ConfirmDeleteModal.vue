<template>
  <div v-if="isOpen" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">Confirm Delete</h3>
        <button class="btn-close" @click="closeModal">✕</button>
      </div>

      <div class="modal-body">
        <div class="warning-icon">⚠️</div>
        <p class="confirm-message">
          Are you sure you want to delete <strong>{{ studentName }}</strong>?
        </p>
        <p class="warning-text">
          This action cannot be undone. All attendance records associated with this student will be permanently deleted.
        </p>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="closeModal">Cancel</button>
        <button class="btn-delete" @click="confirmDelete">Delete Student</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmDeleteModal',
  data() {
    return {
      isOpen: false,
      studentName: '',
      resolveCallback: null
    };
  },
  methods: {
    openModal(studentName) {
      this.studentName = studentName;
      this.isOpen = true;
    },
    closeModal() {
      this.isOpen = false;
      this.studentName = '';
      if (this.resolveCallback) {
        this.resolveCallback(false);
        this.resolveCallback = null;
      }
    },
    confirmDelete() {
      this.isOpen = false;
      if (this.resolveCallback) {
        this.resolveCallback(true);
        this.resolveCallback = null;
      }
    },
    /**
     * Promise-based modal confirmation
     * @param {string} studentName - Name of the student to delete
     * @returns {Promise<boolean>} - Resolves with true if confirmed, false if cancelled
     */
    confirm(studentName) {
      return new Promise((resolve) => {
        this.resolveCallback = resolve;
        this.openModal(studentName);
      });
    }
  }
};
</script>

<style scoped>
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
  animation: fadeIn 0.2s ease-out;
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
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 450px;
  width: 90%;
  animation: slideUp 0.3s ease-out;
  overflow: hidden;
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
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-gray);
  background-color: #fafafa;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--dark-gray);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-light);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--dark-gray);
}

.modal-body {
  padding: 32px 24px;
  text-align: center;
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-message {
  font-size: 16px;
  font-weight: 600;
  color: var(--dark-gray);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.warning-text {
  font-size: 14px;
  color: var(--text-light);
  margin: 0;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-gray);
  background-color: #fafafa;
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
  min-width: 100px;
}

.btn-cancel {
  background-color: var(--border-gray);
  color: var(--dark-gray);
}

.btn-cancel:hover {
  background-color: #d0d0d0;
  transform: translateY(-2px);
}

.btn-delete {
  background-color: var(--error-red);
  color: var(--white);
}

.btn-delete:hover {
  background-color: #c82333;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
  transform: translateY(-2px);
}

.btn-delete:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 480px) {
  .modal-content {
    width: 95%;
  }

  .modal-body {
    padding: 24px 16px;
  }

  .modal-header,
  .modal-footer {
    padding: 16px;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-delete {
    width: 100%;
  }

  .warning-icon {
    font-size: 40px;
  }

  .modal-title {
    font-size: 16px;
  }

  .confirm-message {
    font-size: 14px;
  }

  .warning-text {
    font-size: 12px;
  }
}
</style>
