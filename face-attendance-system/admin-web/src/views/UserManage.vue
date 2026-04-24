<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>员工管理</span>
        <el-button type="primary" @click="openCreate">新增员工</el-button>
      </div>
    </template>

    <div class="filters">
      <el-input v-model="query.keyword" placeholder="搜索姓名/工号" style="width: 220px" />
      <el-button @click="fetchUsers">搜索</el-button>
    </div>

    <el-table :data="items" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="employee_no" label="工号" />
      <el-table-column prop="department" label="部门" />
      <el-table-column prop="is_face_registered" label="人脸注册">
        <template #default="{ row }">{{ row.is_face_registered ? "已注册" : "未注册" }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">{{ row.status ? "启用" : "禁用" }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="disable(row)">禁用</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 16px"
      layout="prev, pager, next, total"
      :total="total"
      :page-size="query.size"
      :current-page="query.page"
      @current-change="(page) => { query.page = page; fetchUsers(); }"
    />
  </el-card>

  <el-dialog v-model="dialog.visible" :title="dialog.mode === 'create' ? '新增员工' : '编辑员工'" width="420px">
    <el-form :model="dialog.form" label-width="80">
      <el-form-item label="姓名"><el-input v-model="dialog.form.name" /></el-form-item>
      <el-form-item label="工号"><el-input v-model="dialog.form.employee_no" /></el-form-item>
      <el-form-item label="部门"><el-input v-model="dialog.form.department" /></el-form-item>
      <el-form-item label="手机"><el-input v-model="dialog.form.phone" /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialog.visible = false">取消</el-button>
      <el-button type="primary" @click="save">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { createUser, disableUser, getUsers, updateUser } from "../api/admin";

const items = ref([]);
const total = ref(0);

const query = reactive({ page: 1, size: 10, keyword: "" });
const dialog = reactive({
  visible: false,
  mode: "create",
  id: null,
  form: { name: "", employee_no: "", department: "", phone: "" },
});

const fetchUsers = async () => {
  const result = await getUsers(query);
  items.value = result.data.items;
  total.value = result.data.total;
};

const resetForm = () => {
  dialog.form = { name: "", employee_no: "", department: "", phone: "" };
};

const openCreate = () => {
  dialog.mode = "create";
  dialog.id = null;
  resetForm();
  dialog.visible = true;
};

const openEdit = (row) => {
  dialog.mode = "edit";
  dialog.id = row.id;
  dialog.form = {
    name: row.name,
    employee_no: row.employee_no,
    department: row.department,
    phone: row.phone,
  };
  dialog.visible = true;
};

const save = async () => {
  if (dialog.mode === "create") {
    await createUser(dialog.form);
    ElMessage.success("新增成功");
  } else {
    await updateUser(dialog.id, dialog.form);
    ElMessage.success("更新成功");
  }
  dialog.visible = false;
  fetchUsers();
};

const disable = async (row) => {
  await disableUser(row.id);
  ElMessage.success("已禁用");
  fetchUsers();
};

fetchUsers();
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
</style>
