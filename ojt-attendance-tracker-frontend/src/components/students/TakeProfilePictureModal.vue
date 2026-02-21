<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3>Take Profile Picture</h3>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">

       <!-- Wrap the camera in a div -->
        <div class="webcam-wrapper"  v-show="!photo">
            <vue3-camera ref="webcam" />
        </div>

        <canvas ref="canvas" style="display: none;"></canvas>

        <div class="button-container" v-show="!photo">
          <button @click="capturePhoto" class="capture-btn">Capture Photo</button>
        </div>

        <!-- Show Captured Photo -->
        <div v-if="photo" class="photo-preview">
          <h4>Preview:</h4>
          <img :src="photo" alt="Captured Photo" />

          <button @click="closeModal" class="capture-btn mt-3">Use This Photo</button>
          <button @click="photo = null" class="capture-btn mt-3">Retake Photo</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import Vue3Camera from 'vue3-camera';

export default {
    name: 'TakeProfilePictureModal',
    components: {
        Vue3Camera
    },
    data() {
        return {
            isOpen: false,
            studentId: null,
            photo: null
        };
    },
    emits: ['photo-captured'],
    methods: {
        openModal(studentId) {
            this.studentId = studentId;
            this.isOpen = true;
            this.photo = null; // Reset photo when opening the modal
        },
        closeModal() {

            const video = this.$refs.webcam?.$el?.querySelector('video');
            if (video && video.srcObject) {
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }

            this.isOpen = false;
            this.studentId = null;
            this.photo = null;
        },
       capturePhoto() {
            // Get the video element inside the webcam component
            const video = this.$refs.webcam?.$el?.querySelector('video');
            const canvas = this.$refs.canvas;

            if (!video || !canvas) {
                console.error('Webcam or canvas not ready.');
                return;
            }

            // Match canvas size to video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Draw the current video frame onto the canvas
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to base64 image
            const photo = canvas.toDataURL('image/png');
            this.photo = photo;

            this.$emit('photo-captured', photo);
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
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal Content */
.modal-content {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
  max-width: 850px;
  width: 90%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ff5a5f;
}

/* Modal Body */
.modal-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.webcam-wrapper {
  width: 100%;
  max-width: 1000px;   /* constrain the width */
  max-height: 500px;  /* constrain the height */
  overflow: hidden;
  border-radius: 12px;
  border: 2px solid #ddd;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.webcam-wrapper :deep(video),
.webcam-wrapper :deep(canvas) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover;
  display: block;
}

.webcam-wrapper :deep(button){
    display: none !important;
}

.webcam-wrapper :deep(.snapshot) {
  display: none !important;
}

/* Button Container */
.button-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.capture-btn {
  padding: 10px 24px;
  background-color: #4169E1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.capture-btn:hover {
  background-color: #315AC1;
  transform: translateY(-2px);
}

/* Photo Preview */
.photo-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.photo-preview h4 {
  font-size: 14px;
  color: #333;
  margin: 0;
}

.photo-preview img {
  max-width: 100%;
  border-radius: 8px;
  border: 2px solid #ddd;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Responsive */
@media (max-width: 480px) {
  .modal-content {
    width: 95%;
    padding: 16px;
  }

  .modal-header h3 {
    font-size: 18px;
  }

  .capture-btn {
    width: 100%;
    padding: 12px 0;
  }
}

</style>
