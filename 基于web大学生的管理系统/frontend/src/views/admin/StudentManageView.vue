<template>
  <el-card>
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>学生管理</span>
        <el-button type="primary" @click="openCreate">新增学生</el-button>
      </div>
    </template>

    <el-table :data="students" border>
      <el-table-column prop="studentNo" label="学号" width="120" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="collegeName" label="学院" min-width="160" />
      <el-table-column prop="majorName" label="专业" min-width="160" />
      <el-table-column prop="className" label="班级" min-width="140" />
      <el-table-column prop="totalServiceHours" label="累计时长" width="110" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="visible" title="学生信息" width="640px">
    <el-form :model="form" label-width="100px">
      <el-form-item label="学号">
        <el-input v-model="form.studentNo" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="性别">
        <el-select v-model="form.gender" style="width: 100%;">
          <el-option label="男" value="男" />
          <el-option label="女" value="女" />
        </el-select>
      </el-form-item>
      <el-form-item label="学院">
        <el-input v-model="form.collegeName" />
      </el-form-item>
      <el-form-item label="专业">
        <el-input v-model="form.majorName" />
      </el-form-item>
      <el-form-item label="班级">
        <el-input v-model="form.className" />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item v-if="!editingId" label="初始密码">
        <el-input v-model="form.password" show-password />
      </el-form-item>
      <el-alert
        v-else
        title="编辑学生资料不会改动登录密码"
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
import { createStudent, getStudents, updateStudent } from '../../api/modules/admin';

const students = ref([]);
const visible = ref(false);
const editingId = ref(null);
const form = reactive({});

const resetForm = () => {
  Object.assign(form, {
    studentNo: '',
    name: '',
    gender: '男',
    collegeName: '',
    majorName: '',
    className: '',
    phone: '',
    email: '',
    password: '123456'
  });
};

const load = async () => {
  students.value = await getStudents();
};

const openCreate = () => {
  editingId.value = null;
  resetForm();
  visible.value = true;
};

const openEdit = (row) => {
  editingId.value = row.id;
  Object.assign(form, {
    studentNo: row.studentNo,
    name: row.name,
    gender: row.gender || '男',
    collegeName: row.collegeName,
    majorName: row.majorName,
    className: row.className,
    phone: row.phone,
    email: row.email,
    password: ''
  });
  visible.value = true;
};

const submit = async () => {
  const payload = {
    studentNo: form.studentNo,
    name: form.name,
    gender: form.gender,
    collegeName: form.collegeName,
    majorName: form.majorName,
    className: form.className,
    phone: form.phone,
    email: form.email
  };

  if (editingId.value) {
    await updateStudent(editingId.value, payload);
  } else {
    await createStudent({ ...payload, password: form.password || '123456' });
  }
  ElMessage.success('保存成功');
  visible.value = false;
  await load();
};

onMounted(load);
</script>
