<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>公告管理</span>
        <el-button type="primary" @click="openCreate">发布公告</el-button>
      </div>
    </template>

    <el-table :data="notices" border>
      <el-table-column prop="title" label="标题" min-width="260" />
      <el-table-column prop="publishStatus" label="状态" width="120" />
      <el-table-column prop="publishedAt" label="发布时间" min-width="180" />
      <el-table-column label="附件" min-width="220">
        <template #default="{ row }">
          <el-link v-if="row.attachmentUrl" :href="assetUrl(row.attachmentUrl)" target="_blank" type="primary">
            查看附件
          </el-link>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="公告信息" width="640px">
    <el-form :model="form" label-width="80px">
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="6" />
      </el-form-item>
      <el-form-item label="附件">
        <UploadField
          v-model="form.attachmentUrl"
          upload-path="/files/upload/notice-attachment"
          button-text="上传附件"
        />
      </el-form-item>
      <el-form-item v-if="form.attachmentUrl" label="附件地址">
        <el-link :href="assetUrl(form.attachmentUrl)" target="_blank" type="primary">
          {{ form.attachmentUrl }}
        </el-link>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { createNotice, getNotices, updateNotice } from '../../api/modules/admin';
import UploadField from '../../components/UploadField.vue';

const notices = ref([]);
const visible = ref(false);
const editingId = ref(null);
const form = reactive({ title: '', content: '', attachmentUrl: '' });

const assetUrl = (value) => {
  if (!value) {
    return '';
  }
  if (value.startsWith('http')) {
    return value;
  }
  return `http://localhost:8080${value}`;
};

const load = async () => {
  notices.value = await getNotices();
};

const openCreate = () => {
  editingId.value = null;
  Object.assign(form, { title: '', content: '', attachmentUrl: '' });
  visible.value = true;
};

const openEdit = (row) => {
  editingId.value = row.id;
  Object.assign(form, {
    title: row.title,
    content: row.content,
    attachmentUrl: row.attachmentUrl || ''
  });
  visible.value = true;
};

const submit = async () => {
  if (editingId.value) {
    await updateNotice(editingId.value, form);
  } else {
    await createNotice(form);
  }
  ElMessage.success('保存成功');
  visible.value = false;
  await load();
};

onMounted(load);
</script>
