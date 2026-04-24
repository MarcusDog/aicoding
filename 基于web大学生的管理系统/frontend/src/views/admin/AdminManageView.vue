<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>管理员管理</span>
        <el-button type="primary" @click="openCreate">新增管理员</el-button>
      </div>
    </template>

    <el-table :data="admins" border>
      <el-table-column prop="adminNo" label="工号" width="120" />
      <el-table-column prop="name" label="姓名" width="110" />
      <el-table-column prop="titleName" label="职务" min-width="160" />
      <el-table-column prop="phone" label="电话" min-width="140" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="管理员信息" width="640px">
    <el-form :model="form" label-width="100px">
      <el-form-item label="工号">
        <el-input v-model="form.adminNo" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="职务">
        <el-input v-model="form.titleName" />
      </el-form-item>
      <el-form-item v-if="!editingId" label="初始密码">
        <el-input v-model="form.password" show-password />
      </el-form-item>
      <el-alert
        v-else
        title="编辑管理员资料不会改动登录密码"
        type="info"
        :closable="false"
        style="margin-bottom: 12px;"
      />
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
import { createAdmin, getAdmins, updateAdmin } from '../../api/modules/admin';

const admins = ref([]);
const visible = ref(false);
const editingId = ref(null);
const form = reactive({});

const resetForm = () => {
  Object.assign(form, {
    adminNo: '',
    name: '',
    phone: '',
    email: '',
    titleName: '',
    password: '123456'
  });
};

const load = async () => {
  admins.value = await getAdmins();
};

const openCreate = () => {
  editingId.value = null;
  resetForm();
  visible.value = true;
};

const openEdit = (row) => {
  editingId.value = row.id;
  Object.assign(form, {
    adminNo: row.adminNo,
    name: row.name,
    phone: row.phone,
    email: row.email,
    titleName: row.titleName,
    password: ''
  });
  visible.value = true;
};

const submit = async () => {
  const payload = {
    adminNo: form.adminNo,
    name: form.name,
    phone: form.phone,
    email: form.email,
    titleName: form.titleName
  };

  if (editingId.value) {
    await updateAdmin(editingId.value, payload);
  } else {
    await createAdmin({ ...payload, password: form.password || '123456' });
  }
  ElMessage.success('保存成功');
  visible.value = false;
  await load();
};

onMounted(load);
</script>
