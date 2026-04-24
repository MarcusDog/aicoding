<template>
  <div>
    <el-upload
      :show-file-list="false"
      :http-request="handleUpload"
      accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
    >
      <el-button type="primary" plain>{{ buttonText }}</el-button>
    </el-upload>
    <div v-if="modelValue" style="margin-top: 8px; color: #2563eb; word-break: break-all;">
      {{ modelValue }}
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus';
import { uploadFile } from '../api/modules/file';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  uploadPath: {
    type: String,
    required: true
  },
  buttonText: {
    type: String,
    default: '上传文件'
  }
});

const emit = defineEmits(['update:modelValue']);

const handleUpload = async ({ file }) => {
  try {
    const result = await uploadFile(props.uploadPath, file);
    emit('update:modelValue', result.url);
    ElMessage.success('上传成功');
  } catch (error) {
    ElMessage.error(error.message || '上传失败');
  }
};
</script>
