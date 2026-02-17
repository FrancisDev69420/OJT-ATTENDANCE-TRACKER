# StudentForm Component Guide

## Overview
The `StudentForm.vue` component is a professional, fully-featured form for creating and editing student records. It includes validation, error handling, and a beautiful royal blue and orange color theme.

## Features

### ✨ Key Features
- **Create & Edit Modes** - Create new students or edit existing ones
- **Form Validation** - Client-side and server-side validation
- **Axios Integration** - Direct API communication with Laravel backend
- **Error Handling** - Detailed error messages for validation failures
- **Success Notifications** - Auto-dismissing success messages
- **Responsive Design** - Mobile-friendly layout
- **Loading States** - Disabled inputs during API calls
- **Real-time Error Clearing** - Errors disappear as user corrects inputs

### 🎨 Color Theme
- **Royal Blue** (#4169E1) - Primary color for headers, buttons, borders
- **Orange** (#FF8C00) - Accent color for required fields, dividers
- **Plain Colors** - No gradients, pure solid colors

## Component Props

```javascript
{
  studentId: {
    type: String,
    default: null,
    description: 'Student ID for edit mode. Leave null for create mode'
  },
  apiBaseUrl: {
    type: String,
    default: 'http://localhost:8000/api',
    description: 'Base URL for API calls'
  }
}
```

## Form Fields

### 1. Student Name
- **Type**: Text input
- **Required**: Yes
- **Validation**: Non-empty string, max 255 characters
- **Placeholder**: "Enter student full name"

### 2. Required Hours
- **Type**: Number input
- **Required**: Yes
- **Validation**: Greater than 0
- **Placeholder**: "e.g., 360"

### 3. Start Date
- **Type**: Date input
- **Required**: Yes
- **Validation**: Valid date format
- **No constraints**: Can be any date

### 4. End Date
- **Type**: Date input
- **Required**: Yes
- **Validation**: Valid date, must be >= start date

## Usage Examples

### 1. Create New Student Form
```vue
<template>
  <StudentForm 
    @student-saved="onStudentSaved"
  />
</template>

<script>
import StudentForm from '@/components/students/StudentForm.vue';

export default {
  components: { StudentForm },
  methods: {
    onStudentSaved(student) {
      console.log('Student created:', student);
      // Refresh your student list or navigate
    }
  }
};
</script>
```

### 2. Edit Student Form
```vue
<template>
  <StudentForm 
    :studentId="editingStudentId"
    @student-saved="onStudentUpdated"
    @cancel="onCancel"
  />
</template>

<script>
import StudentForm from '@/components/students/StudentForm.vue';

export default {
  components: { StudentForm },
  data() {
    return {
      editingStudentId: '550e8400-e29b-41d4-a716-446655440000'
    };
  },
  methods: {
    onStudentUpdated(student) {
      console.log('Student updated:', student);
      this.editingStudentId = null;
    },
    onCancel() {
      this.editingStudentId = null;
    }
  }
};
</script>
```

### 3. Custom API Base URL
```vue
<template>
  <StudentForm 
    apiBaseUrl="https://api.yourdomain.com/api"
  />
</template>
```

## Events

### `student-saved`
Emitted when a student is successfully created or updated.

```javascript
@student-saved="handleStudentSaved"

methods: {
  handleStudentSaved(student) {
    // student object contains: id, name, required_hours, start_date, end_date, created_at, updated_at
  }
}
```

### `cancel`
Emitted when user clicks Cancel in edit mode.

```javascript
@cancel="handleCancel"
```

## API Integration

The component automatically communicates with these endpoints:

### Create Student
```
POST /api/students
Content-Type: application/json

{
  "name": "John Doe",
  "required_hours": 360,
  "start_date": "2026-02-17",
  "end_date": "2026-05-17"
}
```

### Update Student
```
PUT /api/students/{studentId}
Content-Type: application/json

{
  "name": "John Doe Updated",
  "required_hours": 400,
  "start_date": "2026-02-17",
  "end_date": "2026-06-17"
}
```

### Load Student (Edit Mode)
```
GET /api/students/{studentId}
```

## Validation

### Client-side Validation
- Name: Required, non-empty, max 255 characters
- Required Hours: Required, must be > 0
- Start Date: Required, valid date
- End Date: Required, valid date, >= start date

### Server-side Validation
The Laravel backend validates:
- Name: required, string, max 255
- Required Hours: required, integer
- Start Date: required, date format
- End Date: required, date format, after_or_equal:start_date

## Styling Customization

### Override Colors
```css
<style scoped>
:root {
  --royal-blue: #4169E1;
  --orange: #FF8C00;
  /* Change other colors as needed */
}
</style>
```

### CSS Classes Available
- `.student-form-container` - Main container
- `.form-card` - Card wrapper
- `.form-header` - Header section
- `.form-title` - Title element
- `.form-group` - Individual form field
- `.form-input` - Input elements
- `.btn-primary` - Primary button
- `.btn-secondary` - Secondary button
- `.success-message` - Success notification
- `.error-banner` - Error notification

## Error Handling

### Validation Errors
Displayed inline under each field with red border and error text.

### Server Errors (422)
Handled automatically and displayed under respective fields.

### Other Errors (4xx, 5xx)
Displayed in a general error banner at the bottom of the form.

## States

### Normal State
- Form fields are enabled and ready for input
- Buttons are clickable

### Loading State
- Form inputs are disabled
- Buttons show "Loading..." text
- Buttons are disabled

### Error State
- Fields with errors have red borders
- Error messages appear below fields
- General errors appear in a banner
- Form remains editable to allow corrections

### Success State
- Green success message appears
- Auto-dismisses after 3 seconds
- Form is cleared (create mode) or remains filled (edit mode)

## Mobile Responsiveness

The form is fully responsive:
- Desktop: 500px max-width
- Tablet: Full width with padding
- Mobile: Stack buttons vertically

## Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE11: Not supported (modern Vue 3 requirement)

## Integration with Parent Routes

### Create Page
```vue
<template>
  <div>
    <h2>Register New Student</h2>
    <StudentForm @student-saved="navigateToStudentsList" />
  </div>
</template>
```

### Edit Page (with Router)
```vue
<template>
  <div>
    <h2>Edit Student</h2>
    <StudentForm 
      :studentId="$route.params.id"
      @student-saved="navigateToStudentDetail"
      @cancel="$router.back()"
    />
  </div>
</template>
```

## Troubleshooting

### Form not submitting
- Check browser console for errors
- Verify API endpoint is accessible
- Ensure CORS is enabled on Laravel backend

### Validation errors not clearing
- Check that watchers are working (check Vue DevTools)
- Verify form fields are bound with v-model

### Axios not working
- Install axios: `npm install axios`
- Configure axios in main.js if using interceptors
- Check network tab in DevTools for API calls

### Styling issues
- Check that CSS is loaded properly
- Verify no conflicting global styles
- Use browser DevTools to inspect elements

## Performance Tips

1. **Memoize computed properties** if form is complex
2. **Debounce validation** if adding real-time validation
3. **Lazy load** the component if not always needed
4. **Optimize images** if adding file uploads later

## Future Enhancements

Potential improvements:
- Add file upload for student photo
- Add optional fields (phone, email)
- Add instructor/department selection
- Add custom validation rules
- Add drag-and-drop for dates
- Add date range picker
- Add auto-save drafts
- Add keyboard shortcuts (Ctrl+S to save)
