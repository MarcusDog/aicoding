<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>活动管理</span>
        <el-button type="primary" @click="openCreate">新建活动</el-button>
      </div>
    </template>

    <el-table :data="activities" border>
      <el-table-column prop="title" label="活动名称" min-width="220" />
      <el-table-column prop="categoryCode" label="类别" width="120" />
      <el-table-column prop="location" label="地点" min-width="150" />
      <el-table-column prop="recruitCount" label="人数上限" width="100" />
      <el-table-column prop="activityStatus" label="状态" width="120" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button
            link
            type="success"
            :disabled="row.activityStatus !== 'DRAFT'"
            @click="handlePublish(row.id)"
          >
            发布
          </el-button>
          <el-button
            link
            type="danger"
            :disabled="row.activityStatus === 'CANCELLED'"
            @click="handleCancel(row.id)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="活动信息" width="720px">
    <el-form :model="form" label-width="110px">
      <el-form-item label="活动名称">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="活动类别">
        <el-select v-model="form.categoryCode" style="width: 100%;">
          <el-option label="校园服务" value="CAMPUS" />
          <el-option label="社区服务" value="COMMUNITY" />
          <el-option label="公益宣传" value="PUBLICITY" />
          <el-option label="赛事服务" value="EVENT" />
        </el-select>
      </el-form-item>
      <el-form-item label="活动地点">
        <el-input v-model="form.location" />
      </el-form-item>
      <el-form-item label="组织单位">
        <el-input v-model="form.organizerName" />
      </el-form-item>
      <el-form-item label="人数上限">
        <el-input-number v-model="form.recruitCount" :min="1" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="报名截止">
        <el-date-picker
          v-model="form.signupDeadline"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item label="开始时间">
        <el-date-picker
          v-model="form.startTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item label="结束时间">
        <el-date-picker
          v-model="form.endTime"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%;"
        />
      </el-form-item>
      <el-form-item label="服务时长">
        <el-input-number v-model="form.serviceHours" :min="0.5" :step="0.5" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="活动封面">
        <UploadField
          v-model="form.coverUrl"
          upload-path="/files/upload/activity-cover"
          button-text="上传封面"
        />
      </el-form-item>
      <el-form-item v-if="form.coverUrl" label="封面预览">
        <el-image
          :src="coverPreviewUrl"
          fit="cover"
          style="width: 180px; height: 110px; border-radius: 8px;"
          :preview-src-list="[coverPreviewUrl]"
        />
      </el-form-item>
      <el-form-item label="活动附件">
        <UploadField
          v-model="form.attachmentUrl"
          upload-path="/files/upload/activity-attachment"
          button-text="上传附件"
        />
      </el-form-item>
      <el-form-item v-if="form.attachmentUrl" label="附件地址">
        <el-link :href="assetUrl(form.attachmentUrl)" target="_blank" type="primary">
          {{ form.attachmentUrl }}
        </el-link>
      </el-form-item>
      <el-form-item label="活动描述">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { cancelActivity, createActivity, getActivities, publishActivity, updateActivity } from '../../api/modules/admin';
import UploadField from '../../components/UploadField.vue';

const activities = ref([]);
const visible = ref(false);
const editingId = ref(null);
const form = reactive({});

const assetUrl = (value) => {
  if (!value) {
    return '';
  }
  if (value.startsWith('http')) {
    return value;
  }
  return `http://localhost:8080${value}`;
};

const coverPreviewUrl = computed(() => assetUrl(form.coverUrl));

const resetForm = () => {
  Object.assign(form, {
    title: '',
    categoryCode: 'CAMPUS',
    location: '',
    organizerName: '',
    recruitCount: 10,
    signupDeadline: '',
    startTime: '',
    endTime: '',
    serviceHours: 2,
    description: '',
    coverUrl: '',
    attachmentUrl: ''
  });
};

const load = async () => {
  activities.value = await getActivities();
};

const openCreate = () => {
  editingId.value = null;
  resetForm();
  visible.value = true;
};

const openEdit = (row) => {
  editingId.value = row.id;
  Object.assign(form, {
    ...row,
    coverUrl: row.coverUrl || '',
    attachmentUrl: row.attachmentUrl || ''
  });
  visible.value = true;
};

const submit = async () => {
  if (editingId.value) {
    await updateActivity(editingId.value, form);
  } else {
    await createActivity(form);
  }
  ElMessage.success('保存成功');
  visible.value = false;
  await load();
};

const handlePublish = async (id) => {
  await publishActivity(id);
  ElMessage.success('发布成功');
  await load();
};

const handleCancel = async (id) => {
  await cancelActivity(id);
  ElMessage.success('取消成功');
  await load();
};

onMounted(load);
</script>
