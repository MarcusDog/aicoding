<template>
  <el-card>
    <template #header>
      <div class="row">
        <span>签到规则配置</span>
        <el-button type="primary" @click="openCreate">新建规则</el-button>
      </div>
    </template>

    <el-table :data="rules" border v-loading="loading">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="规则名称" />
      <el-table-column label="坐标">
        <template #default="{ row }">{{ row.latitude }}, {{ row.longitude }}</template>
      </el-table-column>
      <el-table-column prop="radius" label="半径(米)" width="100" />
      <el-table-column label="时间段">
        <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
      </el-table-column>
      <el-table-column prop="week_days" label="生效周" />
      <el-table-column prop="is_active" label="启用">
        <template #default="{ row }">{{ row.is_active ? "是" : "否" }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-popconfirm title="确认删除该规则？" @confirm="removeRule(row)">
            <template #reference>
              <el-button size="small" type="danger" plain>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialog.visible" :title="dialog.mode === 'create' ? '新建规则' : '编辑规则'" width="520px">
    <el-form :model="dialog.form" label-width="100">
      <el-form-item label="规则名称"><el-input v-model="dialog.form.name" /></el-form-item>
      <el-form-item label="纬度"><el-input v-model="dialog.form.latitude" /></el-form-item>
      <el-form-item label="经度"><el-input v-model="dialog.form.longitude" /></el-form-item>
      <el-form-item label="半径"><el-input v-model="dialog.form.radius" /></el-form-item>
      <el-form-item label="开始时间"><el-input v-model="dialog.form.start_time" placeholder="08:00:00" /></el-form-item>
      <el-form-item label="结束时间"><el-input v-model="dialog.form.end_time" placeholder="10:00:00" /></el-form-item>
      <el-form-item label="迟到时间"><el-input v-model="dialog.form.late_time" placeholder="08:30:00" /></el-form-item>
      <el-form-item label="生效星期"><el-input v-model="dialog.form.week_days" placeholder="1,2,3,4,5" /></el-form-item>
      <el-form-item label="启用">
        <el-switch v-model="dialog.form.is_active" />
      </el-form-item>
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

import { createRule, deleteRule, getRules, updateRule } from "../api/admin";

const loading = ref(false);
const rules = ref([]);
const dialog = reactive({
  visible: false,
  mode: "create",
  id: null,
  form: {
    name: "",
    latitude: 31.2304,
    longitude: 121.4737,
    radius: 200,
    start_time: "08:00:00",
    end_time: "10:00:00",
    late_time: "08:30:00",
    week_days: "1,2,3,4,5",
    is_active: true,
  },
});

const resetForm = () => {
  dialog.form = {
    name: "",
    latitude: 31.2304,
    longitude: 121.4737,
    radius: 200,
    start_time: "08:00:00",
    end_time: "10:00:00",
    late_time: "08:30:00",
    week_days: "1,2,3,4,5",
    is_active: true,
  };
};

const fetchRules = async () => {
  loading.value = true;
  try {
    const result = await getRules();
    rules.value = result.data || [];
  } catch (error) {
    ElMessage.error(error.message || "加载规则失败");
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  dialog.mode = "create";
  dialog.id = null;
  resetForm();
  dialog.visible = true;
};

const openEdit = (rule) => {
  dialog.mode = "edit";
  dialog.id = rule.id;
  dialog.form = { ...rule };
  dialog.visible = true;
};

const save = async () => {
  try {
    if (dialog.mode === "create") {
      await createRule(dialog.form);
      ElMessage.success("规则已创建");
    } else {
      await updateRule(dialog.id, dialog.form);
      ElMessage.success("规则已更新");
    }
    dialog.visible = false;
    await fetchRules();
  } catch (error) {
    ElMessage.error(error.message || "保存失败");
  }
};

const removeRule = async (rule) => {
  try {
    await deleteRule(rule.id);
    ElMessage.success("规则已删除");
    await fetchRules();
  } catch (error) {
    ElMessage.error(error.message || "删除失败");
  }
};

fetchRules();
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
