import { api } from './api.js';
import {
  demandDraft,
  formatBudget,
  formatDate,
  profileDraft,
  roleText,
  statusClass,
  statusLabel,
  toDemandPayload,
  workspacePath
} from './helpers.js';
import {
  clearMessages,
  flashError,
  flashNotice,
  logoutUser,
  setLoading,
  setUser,
  state
} from './store.js';

const { computed, createApp, reactive, ref, onMounted } = window.Vue;
const { createRouter, createWebHistory, useRoute, useRouter } = window.VueRouter;

async function execute(action, successMessage = '') {
  setLoading(true);
  try {
    const result = await action();
    if (successMessage) flashNotice(successMessage);
    return result;
  } catch (error) {
    flashError(error.message || '请求失败');
    throw error;
  } finally {
    setLoading(false);
  }
}

function cloneDemandForm(source = {}) {
  return {
    ...demandDraft(),
    ...source
  };
}

function cloneProfileForm(source = {}) {
  return {
    ...profileDraft(),
    ...source
  };
}

const StatusBadge = {
  props: {
    status: {
      type: String,
      required: true
    }
  },
  template: `<span class="badge" :class="badgeClass">{{ label }}</span>`,
  setup(props) {
    return {
      badgeClass: computed(() => statusClass(props.status)),
      label: computed(() => statusLabel(props.status))
    };
  }
};

const EmptyState = {
  props: {
    title: { type: String, required: true },
    description: { type: String, required: true }
  },
  template: `
    <div class="empty">
      <strong>{{ title }}</strong>
      <p>{{ description }}</p>
    </div>
  `
};

const DemandCard = {
  components: { StatusBadge },
  props: {
    demand: { type: Object, required: true }
  },
  template: `
    <article class="record">
      <div class="record-head">
        <div>
          <h3>{{ demand.title }}</h3>
          <p>{{ demand.subject }} · {{ demand.gradeLevel }} · {{ demand.location }}</p>
        </div>
        <StatusBadge :status="demand.status" />
      </div>
      <p>{{ demand.description }}</p>
      <div class="record-meta">
        <span>{{ formatBudget(demand) }}</span>
        <span>{{ demand.schedule }}</span>
      </div>
      <router-link class="text-link" :to="'/demands/' + demand.id">查看需求详情</router-link>
    </article>
  `,
  setup() {
    return { formatBudget };
  }
};

const TutorCard = {
  components: { StatusBadge },
  props: {
    profile: { type: Object, required: true }
  },
  template: `
    <article class="record">
      <div class="record-head">
        <div>
          <h3>{{ profile.userName }}</h3>
          <p>{{ profile.school }} · {{ profile.major }} · {{ profile.serviceMode || '服务方式待补充' }}</p>
        </div>
        <StatusBadge :status="profile.status" />
      </div>
      <p>{{ profile.introduction }}</p>
      <p class="helper">教学经验 {{ profile.teachingExperienceYears || 0 }} 年 · 简历 {{ profile.resumeFileName ? '已上传附件' : '仅文本版' }}</p>
      <div class="tag-row">
        <span v-for="subject in subjects" :key="subject" class="tag">{{ subject }}</span>
      </div>
      <router-link class="text-link" :to="'/tutors/' + profile.id">查看教员详情</router-link>
    </article>
  `,
  setup(props) {
    return {
      subjects: computed(() => (props.profile.subjects || '').split(',').map(item => item.trim()).filter(Boolean))
    };
  }
};

const LoginPage = {
  template: `
    <section class="hero auth-hero">
      <div class="hero-copy">
        <div>
          <p class="eyebrow">Welcome</p>
          <h1>登录南华家教</h1>
          <p>管理家教需求、教员认证和服务订单。家长、教员、管理员登录后进入各自工作台。</p>
        </div>
        <div class="action-row">
          <router-link class="button" to="/register">创建账号</router-link>
          <router-link class="button-outline" to="/demands">先看看需求</router-link>
        </div>
      </div>
      <div class="stack">
        <div class="title-row">
          <div>
            <p class="eyebrow">登录</p>
            <h2>进入工作台</h2>
          </div>
          <router-link class="text-link" to="/register">没有账号？去注册</router-link>
        </div>
        <div class="grid-2">
          <form class="panel" @submit.prevent="submit">
            <label class="field">
              <span>用户名</span>
              <input v-model.trim="form.username" autocomplete="username" required />
            </label>
            <label class="field">
              <span>密码</span>
              <input v-model="form.password" type="password" autocomplete="current-password" required />
            </label>
            <button class="button" type="submit">登录</button>
          </form>
          <section class="panel">
            <h2>演示入口</h2>
            <div class="stack">
              <div v-for="demo in demos" :key="demo.username" class="stack-item">
                <div>
                  <strong>{{ demo.label }}</strong>
                  <p class="helper">{{ demo.username }} / {{ demo.password }}</p>
                </div>
                <button class="button-outline" type="button" @click="fillDemo(demo)">填入</button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </section>
  `,
  setup() {
    const router = useRouter();
    const form = reactive({
      username: '',
      password: ''
    });
    const demos = [
      { username: 'parent', password: '123456', label: '家长演示账号' },
      { username: 'tutor', password: '123456', label: '教员演示账号' },
      { username: 'admin', password: '123456', label: '管理员演示账号' },
      { username: 'tutor_pending', password: '123456', label: '待审核教员账号' }
    ];

    function fillDemo(demo) {
      form.username = demo.username;
      form.password = demo.password;
    }

    async function submit() {
      try {
        const user = await execute(() => api.login(form.username, form.password), '登录成功。');
        setUser(user);
        router.push(workspacePath(user));
      } catch {
        // handled globally
      }
    }

    return { demos, fillDemo, form, submit };
  }
};

const RegisterPage = {
  template: `
    <section class="detail-layout">
      <aside class="hero-copy">
        <div>
          <p class="eyebrow">Join</p>
          <h1>注册南华家教</h1>
          <p>家长可以发布辅导需求，教员可以提交认证资料。资料与需求通过审核后再进入匹配流程。</p>
        </div>
        <div class="action-row">
          <router-link class="button-outline" to="/login">已有账号登录</router-link>
          <router-link class="button-outline" to="/tutors">浏览教员库</router-link>
        </div>
      </aside>
      <section class="section flush">
        <div class="title-row">
          <div>
            <p class="eyebrow">注册</p>
            <h2>创建账号</h2>
          </div>
          <router-link class="text-link" to="/login">已有账号？去登录</router-link>
        </div>
        <form class="panel" @submit.prevent="submit">
          <div class="form-grid two">
            <label class="field">
              <span>用户名</span>
              <input v-model.trim="form.username" required />
            </label>
            <label class="field">
              <span>密码</span>
              <input v-model="form.password" type="password" required />
            </label>
            <label class="field">
              <span>姓名</span>
              <input v-model.trim="form.displayName" required />
            </label>
            <label class="field">
              <span>手机号码</span>
              <input v-model.trim="form.phone" required />
            </label>
          </div>
          <label class="field">
            <span>注册角色</span>
            <select v-model="form.role">
              <option value="PARENT">家长</option>
              <option value="TUTOR">教员</option>
            </select>
          </label>
          <button class="button" type="submit">完成注册</button>
        </form>
      </section>
    </section>
  `,
  setup() {
    const router = useRouter();
    const form = reactive({
      username: '',
      password: '',
      displayName: '',
      phone: '',
      role: 'PARENT'
    });

    async function submit() {
      try {
        const user = await execute(() => api.register(form), '注册成功。');
        setUser(user);
        router.push(workspacePath(user));
      } catch {
        // handled globally
      }
    }

    return { form, submit };
  }
};

const DemandListPage = {
  components: { DemandCard, EmptyState },
  template: `
    <section class="section">
      <div class="title-row">
        <div>
          <p class="eyebrow">需求大厅</p>
          <h1>开放中的家教需求</h1>
        </div>
        <router-link class="button-outline" to="/parent">发布需求</router-link>
      </div>
      <div class="record-grid" v-if="demands.length">
        <DemandCard v-for="demand in demands" :key="demand.id" :demand="demand" />
      </div>
      <EmptyState v-else title="暂无开放需求" description="管理员审核通过后，需求会展示在这里。" />
    </section>
  `,
  setup() {
    const demands = ref([]);
    onMounted(async () => {
      try {
        demands.value = await execute(() => api.catalogDemands());
      } catch {
        demands.value = [];
      }
    });
    return { demands };
  }
};

const DemandDetailPage = {
  components: { StatusBadge },
  template: `
    <section class="detail-layout" v-if="demand">
      <article class="panel">
        <div class="record-head">
          <div>
            <p class="eyebrow">需求详情</p>
            <h1>{{ demand.title }}</h1>
            <p class="helper">{{ demand.parentName }} 发布 · {{ formatDate(demand.createdAt) }}</p>
          </div>
          <StatusBadge :status="demand.status" />
        </div>
        <div class="detail-list">
          <div><span>科目</span><strong>{{ demand.subject }}</strong></div>
          <div><span>年级</span><strong>{{ demand.gradeLevel }}</strong></div>
          <div><span>地点</span><strong>{{ demand.location }}</strong></div>
          <div><span>时间</span><strong>{{ demand.schedule }}</strong></div>
          <div><span>预算</span><strong>{{ formatBudget(demand) }}</strong></div>
          <div><span>发布时间</span><strong>{{ formatDate(demand.createdAt) }}</strong></div>
        </div>
        <h2>需求描述</h2>
        <p>{{ demand.description }}</p>
        <p v-if="demand.reviewRemark" class="alert error">审核备注：{{ demand.reviewRemark }}</p>
      </article>
      <aside class="panel">
        <h2>教员申请</h2>
        <form v-if="canApply" @submit.prevent="submit">
          <label class="field">
            <span>申请说明</span>
            <textarea v-model="coverLetter" rows="6" required></textarea>
          </label>
          <button class="button" type="submit">提交接单申请</button>
        </form>
        <template v-else>
          <p class="helper">请使用已认证教员账号登录后申请开放需求。</p>
          <router-link class="button-outline" to="/login">教员登录</router-link>
        </template>
      </aside>
    </section>
  `,
  setup() {
    const router = useRouter();
    const route = useRoute();
    const demand = ref(null);
    const coverLetter = ref('我可以根据学生基础制定分阶段辅导计划，并在首节课后给出学习建议。');

    const canApply = computed(() => state.user?.role === 'TUTOR' && demand.value?.status === 'OPEN');

    async function load() {
      try {
        demand.value = await execute(() => api.demandDetail(route.params.id));
      } catch {
        demand.value = null;
      }
    }

    async function submit() {
      if (!state.user) {
        router.push('/login');
        return;
      }

      try {
        await execute(() => api.applyForDemand(state.user.id, {
          demandId: Number(route.params.id),
          coverLetter: coverLetter.value
        }), '接单申请已提交。');
        router.push('/tutor');
      } catch {
        // handled globally
      }
    }

    onMounted(load);

    return { canApply, coverLetter, demand, formatBudget, formatDate, submit };
  }
};

const TutorListPage = {
  components: { EmptyState, TutorCard },
  template: `
    <section class="section">
      <div class="title-row">
        <div>
          <p class="eyebrow">教员库</p>
          <h1>已通过认证的教员</h1>
        </div>
        <router-link class="button-outline" to="/register">注册教员</router-link>
      </div>
      <div class="record-grid" v-if="profiles.length">
        <TutorCard v-for="profile in profiles" :key="profile.id" :profile="profile" />
      </div>
      <EmptyState v-else title="暂无教员资料" description="教员认证通过后会显示在这里。" />
    </section>
  `,
  setup() {
    const profiles = ref([]);
    onMounted(async () => {
      try {
        profiles.value = await execute(() => api.approvedTutors());
      } catch {
        profiles.value = [];
      }
    });
    return { profiles };
  }
};

const TutorDetailPage = {
  components: { StatusBadge },
  template: `
    <section class="detail-layout" v-if="profile">
      <article class="panel">
        <div class="record-head">
          <div>
            <p class="eyebrow">教员详情</p>
            <h1>{{ profile.userName }}</h1>
            <p class="helper">{{ profile.school }} · {{ profile.major }}</p>
          </div>
          <StatusBadge :status="profile.status" />
        </div>
        <div class="detail-list">
          <div><span>学校</span><strong>{{ profile.school }}</strong></div>
          <div><span>专业</span><strong>{{ profile.major }}</strong></div>
          <div><span>可授科目</span><strong>{{ profile.subjects }}</strong></div>
          <div><span>教学经验</span><strong>{{ profile.teachingExperienceYears || 0 }} 年</strong></div>
          <div><span>服务方式</span><strong>{{ profile.serviceMode || '待补充' }}</strong></div>
          <div><span>提交时间</span><strong>{{ formatDate(profile.createdAt) }}</strong></div>
        </div>
        <h2>个人简介</h2>
        <p>{{ profile.introduction }}</p>
        <h2>简历摘要</h2>
        <p>{{ profile.resumeText }}</p>
        <p v-if="profile.reviewRemark" class="alert error">审核备注：{{ profile.reviewRemark }}</p>
      </article>
      <aside class="panel">
        <h2>职业资料</h2>
        <p class="helper">家长发布需求后，管理员审核上线，教员再提交接单申请。</p>
        <a v-if="profile.resumeFileDownloadUrl" class="button-outline" :href="profile.resumeFileDownloadUrl">下载简历附件</a>
        <router-link class="button" to="/demands">查看家教需求</router-link>
      </aside>
    </section>
  `,
  setup() {
    const route = useRoute();
    const profile = ref(null);

    onMounted(async () => {
      try {
        profile.value = route.path.startsWith('/tutor-users/')
          ? await execute(() => api.tutorProfileByUser(route.params.id))
          : await execute(() => api.tutorProfileDetail(route.params.id));
      } catch {
        profile.value = null;
      }
    });

    return { formatDate, profile };
  }
};

const ParentPage = {
  components: { EmptyState, StatusBadge },
  template: `
    <section class="workspace">
      <form class="panel" @submit.prevent="submitDemand">
        <div class="title-row">
          <h2>{{ editingDemandId ? '修改被驳回需求' : '发布新需求' }}</h2>
          <button v-if="editingDemandId" class="button-outline" type="button" @click="cancelDemandEdit">取消修改</button>
        </div>
        <div class="form-grid two">
          <label class="field"><span>需求标题</span><input v-model.trim="form.title" required /></label>
          <label class="field"><span>科目</span><input v-model.trim="form.subject" required /></label>
          <label class="field"><span>年级</span><input v-model.trim="form.gradeLevel" required /></label>
          <label class="field"><span>地点</span><input v-model.trim="form.location" required /></label>
          <label class="field"><span>预算下限</span><input v-model.number="form.budgetMin" type="number" min="0" required /></label>
          <label class="field"><span>预算上限</span><input v-model.number="form.budgetMax" type="number" min="0" required /></label>
        </div>
        <label class="field"><span>上课时间</span><input v-model.trim="form.schedule" required /></label>
        <label class="field"><span>需求描述</span><textarea v-model.trim="form.description" rows="5" required></textarea></label>
        <button class="button" type="submit">{{ editingDemandId ? '修改后重新提交' : '提交审核' }}</button>
      </form>

      <div class="stack">
        <section class="panel">
          <div class="title-row">
            <h2>我的需求</h2>
            <span class="muted">{{ demands.length }} 条</span>
          </div>
          <div class="stack" v-if="demands.length">
            <article v-for="item in demands" :key="item.id" class="stack-item">
              <div class="grow">
                <div class="inline-row">
                  <strong>{{ item.title }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p class="helper">{{ item.subject }} · {{ item.gradeLevel }} · {{ formatBudget(item) }}</p>
                <p v-if="item.reviewRemark" class="alert error">审核备注：{{ item.reviewRemark }}</p>
              </div>
              <div class="actions">
                <router-link class="text-link" :to="'/demands/' + item.id">查看</router-link>
                <button v-if="item.status === 'REJECTED'" class="button-outline" type="button" @click="startDemandEdit(item)">修改后重新提交</button>
              </div>
            </article>
          </div>
          <EmptyState v-else title="还没有需求" description="填写左侧表单后提交审核。" />
        </section>

        <section class="panel">
          <div class="title-row">
            <h2>我的订单</h2>
            <span class="muted">{{ orders.length }} 条</span>
          </div>
          <div class="stack" v-if="orders.length">
            <article v-for="order in orders" :key="order.id" class="stack-item">
              <div>
                <div class="inline-row">
                  <strong>{{ order.demandTitle }}</strong>
                  <StatusBadge :status="order.status" />
                </div>
                <p class="helper">{{ order.parentName || '' }} / {{ order.tutorName || '' }} · {{ formatDate(order.createdAt) }}</p>
              </div>
            </article>
          </div>
          <EmptyState v-else title="暂无订单" description="申请通过后自动生成订单。" />
        </section>
      </div>
    </section>
  `,
  setup() {
    const demands = ref([]);
    const orders = ref([]);
    const editingDemandId = ref(null);
    const form = reactive(cloneDemandForm());

    async function load() {
      if (!state.user) return;
      try {
        const [parentDemands, parentOrders] = await execute(() => Promise.all([
          api.parentDemands(state.user.id),
          api.parentOrders(state.user.id)
        ]));
        demands.value = parentDemands;
        orders.value = parentOrders;
      } catch {
        demands.value = [];
        orders.value = [];
      }
    }

    function resetForm() {
      editingDemandId.value = null;
      Object.assign(form, cloneDemandForm());
    }

    function startDemandEdit(item) {
      editingDemandId.value = item.id;
      Object.assign(form, cloneDemandForm(item));
      flashNotice('已载入被驳回需求，请修改后重新提交。');
    }

    function cancelDemandEdit() {
      resetForm();
    }

    async function submitDemand() {
      try {
        const payload = toDemandPayload(form);
        if (editingDemandId.value) {
          await execute(() => api.resubmitDemand(state.user.id, editingDemandId.value, payload), '需求已重新提交审核。');
        } else {
          await execute(() => api.publishDemand(state.user.id, payload), '需求已提交审核。');
        }
        resetForm();
        await load();
      } catch {
        // handled globally
      }
    }

    onMounted(load);

    return {
      cancelDemandEdit,
      demands,
      editingDemandId,
      form,
      formatBudget,
      formatDate,
      orders,
      startDemandEdit,
      submitDemand
    };
  }
};

const TutorPage = {
  components: { EmptyState, StatusBadge },
  template: `
    <section class="workspace">
      <section class="panel">
        <div class="title-row">
          <h2>认证资料</h2>
          <StatusBadge v-if="profile" :status="profile.status" />
        </div>

        <div v-if="profile && !editingProfile">
          <div class="detail-list">
            <div><span>学校</span><strong>{{ profile.school }}</strong></div>
            <div><span>专业</span><strong>{{ profile.major }}</strong></div>
            <div><span>科目</span><strong>{{ profile.subjects }}</strong></div>
            <div><span>教学经验</span><strong>{{ profile.teachingExperienceYears || 0 }} 年</strong></div>
            <div><span>服务方式</span><strong>{{ profile.serviceMode || '待补充' }}</strong></div>
            <div><span>提交时间</span><strong>{{ formatDate(profile.createdAt) }}</strong></div>
          </div>
          <p class="helper">{{ profile.introduction }}</p>
          <p class="helper">{{ profile.resumeText }}</p>
          <div class="action-row" v-if="profile.resumeFileDownloadUrl">
            <a class="button-outline" :href="profile.resumeFileDownloadUrl">下载当前简历附件</a>
            <span class="helper">{{ profile.resumeFileName }}</span>
          </div>
          <p v-if="profile.reviewRemark" class="alert error">审核备注：{{ profile.reviewRemark }}</p>
          <button v-if="profile.status === 'REJECTED'" class="button" type="button" @click="startProfileEdit">修改资料并重新提交</button>
        </div>

        <form v-else @submit.prevent="submitProfile">
          <div class="title-row">
            <h3>{{ editingProfile ? '重新提交认证资料' : '提交认证资料' }}</h3>
            <button v-if="editingProfile" class="button-outline" type="button" @click="cancelProfileEdit">取消修改</button>
          </div>
          <div class="form-grid two">
            <label class="field"><span>学校</span><input v-model.trim="profileForm.school" required /></label>
            <label class="field"><span>专业</span><input v-model.trim="profileForm.major" required /></label>
            <label class="field"><span>教学经验（年）</span><input v-model.number="profileForm.teachingExperienceYears" type="number" min="0" required /></label>
            <label class="field">
              <span>服务方式</span>
              <select v-model="profileForm.serviceMode">
                <option value="线上">线上</option>
                <option value="线下">线下</option>
                <option value="线上+线下">线上+线下</option>
              </select>
            </label>
          </div>
          <label class="field"><span>可授科目</span><input v-model.trim="profileForm.subjects" required /></label>
          <label class="field"><span>个人简介</span><textarea v-model.trim="profileForm.introduction" rows="5" required></textarea></label>
          <label class="field"><span>文字简历</span><textarea v-model.trim="profileForm.resumeText" rows="7" required></textarea></label>
          <button class="button" type="submit">{{ editingProfile ? '修改后重新提交' : '提交认证资料' }}</button>
        </form>
      </section>

      <div class="stack">
        <section class="panel">
          <div class="title-row">
            <h2>简历附件</h2>
            <span class="muted">{{ profile?.resumeFileName ? '已上传' : '未上传' }}</span>
          </div>
          <label class="field">
            <span>上传文件（pdf/doc/docx/txt）</span>
            <input type="file" accept=".pdf,.doc,.docx,.txt" @change="onResumeFileChange" />
          </label>
          <div class="action-row">
            <button class="button" type="button" :disabled="!resumeFile" @click="uploadResumeFile">上传简历附件</button>
            <a v-if="profile?.resumeFileDownloadUrl" class="button-outline" :href="profile.resumeFileDownloadUrl">下载已上传附件</a>
          </div>
          <p class="helper" v-if="resumeFile">待上传文件：{{ resumeFile.name }}</p>
          <p class="helper" v-else-if="profile?.resumeFileName">当前文件：{{ profile.resumeFileName }}</p>
          <p class="helper">建议上传完整简历、获奖证明或教学案例摘要，便于管理员审核。</p>
        </section>

        <section class="panel">
          <div class="title-row">
            <h2>开放需求</h2>
            <span class="muted">{{ demands.length }} 条</span>
          </div>
          <div class="stack" v-if="demands.length">
            <article v-for="item in demands" :key="item.id" class="stack-item">
              <div>
                <strong>{{ item.title }}</strong>
                <p class="helper">{{ item.subject }} · {{ item.location }} · {{ formatBudget(item) }}</p>
              </div>
              <router-link class="text-link" :to="'/demands/' + item.id">查看</router-link>
            </article>
          </div>
          <EmptyState v-else title="暂无开放需求" description="审核通过的需求会显示在这里。" />
        </section>

        <section class="panel">
          <div class="title-row">
            <h2>我的申请</h2>
            <span class="muted">{{ applications.length }} 条</span>
          </div>
          <div class="stack" v-if="applications.length">
            <article v-for="item in applications" :key="item.id" class="stack-item">
              <div>
                <div class="inline-row">
                  <strong>{{ item.demandTitle }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p class="helper">{{ item.coverLetter }}</p>
                <p v-if="item.reviewRemark" class="alert error">审核备注：{{ item.reviewRemark }}</p>
              </div>
              <router-link class="text-link" :to="'/demands/' + item.demandId">查看需求</router-link>
            </article>
          </div>
          <EmptyState v-else title="暂无申请" description="进入需求详情页可以提交申请。" />
        </section>

        <section class="panel">
          <div class="title-row">
            <h2>我的订单</h2>
            <span class="muted">{{ orders.length }} 条</span>
          </div>
          <div class="stack" v-if="orders.length">
            <article v-for="order in orders" :key="order.id" class="stack-item">
              <div>
                <div class="inline-row">
                  <strong>{{ order.demandTitle }}</strong>
                  <StatusBadge :status="order.status" />
                </div>
                <p class="helper">{{ order.parentName || '' }} / {{ order.tutorName || '' }} · {{ formatDate(order.createdAt) }}</p>
              </div>
            </article>
          </div>
          <EmptyState v-else title="暂无订单" description="申请通过后会生成订单。" />
        </section>
      </div>
    </section>
  `,
  setup() {
    const profile = ref(null);
    const demands = ref([]);
    const applications = ref([]);
    const orders = ref([]);
    const editingProfile = ref(false);
    const resumeFile = ref(null);
    const profileForm = reactive(cloneProfileForm());

    async function load() {
      if (!state.user) return;

      try {
        profile.value = await api.tutorProfile(state.user.id);
        Object.assign(profileForm, cloneProfileForm(profile.value));
      } catch {
        profile.value = null;
        Object.assign(profileForm, cloneProfileForm());
      }

      try {
        const [openDemands, tutorApplications, tutorOrders] = await execute(() => Promise.all([
          api.catalogDemands(),
          api.tutorApplications(state.user.id),
          api.tutorOrders(state.user.id)
        ]));
        demands.value = openDemands;
        applications.value = tutorApplications;
        orders.value = tutorOrders;
      } catch {
        demands.value = [];
        applications.value = [];
        orders.value = [];
      }
    }

    function startProfileEdit() {
      editingProfile.value = true;
      Object.assign(profileForm, cloneProfileForm(profile.value || {}));
      flashNotice('请根据审核备注修改资料后重新提交。');
    }

    function cancelProfileEdit() {
      editingProfile.value = false;
      Object.assign(profileForm, cloneProfileForm(profile.value || {}));
    }

    function onResumeFileChange(event) {
      resumeFile.value = event.target.files?.[0] || null;
    }

    async function submitProfile() {
      try {
        if (editingProfile.value) {
          profile.value = await execute(() => api.resubmitTutorProfile(state.user.id, profileForm), '教员资料已重新提交审核。');
        } else {
          profile.value = await execute(() => api.submitTutorProfile(state.user.id, profileForm), '教员资料已提交审核。');
        }
        editingProfile.value = false;
        Object.assign(profileForm, cloneProfileForm(profile.value || {}));
        await load();
      } catch {
        // handled globally
      }
    }

    async function uploadResumeFile() {
      if (!resumeFile.value) return;
      try {
        profile.value = await execute(() => api.uploadTutorResumeFile(state.user.id, resumeFile.value), '简历附件已上传。');
        resumeFile.value = null;
        await load();
      } catch {
        // handled globally
      }
    }

    onMounted(load);

    return {
      applications,
      cancelProfileEdit,
      demands,
      editingProfile,
      formatBudget,
      formatDate,
      onResumeFileChange,
      orders,
      profile,
      profileForm,
      resumeFile,
      startProfileEdit,
      uploadResumeFile,
      submitProfile
    };
  }
};

const AdminPage = {
  components: { EmptyState, StatusBadge },
  template: `
    <div>
      <section class="section">
        <div class="title-row">
          <div>
            <p class="eyebrow">管理后台</p>
            <h1>{{ state.user?.displayName }} 的审核工作台</h1>
          </div>
        </div>
        <div class="metric-grid">
          <article v-for="metric in metrics" :key="metric.label" class="metric">
            <strong>{{ metric.value }}</strong>
            <span>{{ metric.label }}</span>
          </article>
        </div>
      </section>

      <section class="workspace">
        <section class="panel">
          <div class="title-row"><h2>教员资料审核</h2></div>
          <div class="stack" v-if="profiles.length">
            <article v-for="profile in profiles" :key="profile.id" class="stack-item">
              <div class="grow">
                <div class="inline-row">
                  <strong>{{ profile.userName }}</strong>
                  <StatusBadge :status="profile.status" />
                </div>
                <p class="helper">{{ profile.school }} · {{ profile.major }} · {{ profile.subjects }}</p>
                <p class="helper">教学经验 {{ profile.teachingExperienceYears || 0 }} 年 · {{ profile.serviceMode || '待补充' }}</p>
                <p class="helper" v-if="profile.resumeFileName">附件：{{ profile.resumeFileName }}</p>
                <label class="field">
                  <span>审核备注</span>
                  <textarea v-model="remarks['profile-' + profile.id]" rows="2"></textarea>
                </label>
              </div>
              <div class="actions">
                <router-link class="text-link" :to="'/tutors/' + profile.id">查看</router-link>
                <a v-if="profile.resumeFileDownloadUrl" class="text-link" :href="profile.resumeFileDownloadUrl">简历附件</a>
                <button class="button" type="button" @click="auditProfile(profile.id, true)">通过</button>
                <button class="button-outline danger" type="button" @click="auditProfile(profile.id, false)">驳回</button>
              </div>
            </article>
          </div>
          <EmptyState v-else title="暂无记录" description="当前没有待处理的教员资料。" />
        </section>

        <section class="panel">
          <div class="title-row"><h2>需求审核</h2></div>
          <div class="stack" v-if="demands.length">
            <article v-for="item in demands" :key="item.id" class="stack-item">
              <div class="grow">
                <div class="inline-row">
                  <strong>{{ item.title }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p class="helper">{{ item.parentName }} · {{ item.subject }} · {{ item.gradeLevel }}</p>
                <label class="field">
                  <span>审核备注</span>
                  <textarea v-model="remarks['demand-' + item.id]" rows="2"></textarea>
                </label>
              </div>
              <div class="actions">
                <router-link class="text-link" :to="'/demands/' + item.id">查看</router-link>
                <button class="button" type="button" @click="auditDemand(item.id, true)">通过</button>
                <button class="button-outline danger" type="button" @click="auditDemand(item.id, false)">驳回</button>
              </div>
            </article>
          </div>
          <EmptyState v-else title="暂无记录" description="当前没有待处理的家教需求。" />
        </section>

        <section class="panel">
          <div class="title-row"><h2>接单申请审核</h2></div>
          <div class="stack" v-if="applications.length">
            <article v-for="item in applications" :key="item.id" class="stack-item">
              <div class="grow">
                <div class="inline-row">
                  <strong>{{ item.demandTitle }}</strong>
                  <StatusBadge :status="item.status" />
                </div>
                <p class="helper">教员：{{ item.tutorName }}。{{ item.coverLetter }}</p>
                <label class="field">
                  <span>审核备注</span>
                  <textarea v-model="remarks['application-' + item.id]" rows="2"></textarea>
                </label>
              </div>
              <div class="actions">
                <router-link class="text-link" :to="'/tutor-users/' + item.tutorId + '/profile'">教员</router-link>
                <router-link class="text-link" :to="'/demands/' + item.demandId">需求</router-link>
                <button class="button" type="button" @click="reviewApplication(item.id, true)">通过</button>
                <button class="button-outline danger" type="button" @click="reviewApplication(item.id, false)">驳回</button>
              </div>
            </article>
          </div>
          <EmptyState v-else title="暂无记录" description="当前没有待处理的接单申请。" />
        </section>

        <section class="panel">
          <div class="title-row"><h2>订单与审核记录</h2></div>
          <div class="stack" v-if="orders.length">
            <article v-for="order in orders" :key="order.id" class="stack-item">
              <div>
                <div class="inline-row">
                  <strong>{{ order.demandTitle }}</strong>
                  <StatusBadge :status="order.status" />
                </div>
                <p class="helper">{{ order.parentName || '' }} / {{ order.tutorName || '' }} · {{ formatDate(order.createdAt) }}</p>
              </div>
            </article>
          </div>
          <hr />
          <div class="stack" v-if="audits.length">
            <article v-for="audit in audits" :key="audit.id" class="stack-item">
              <div>
                <div class="inline-row">
                  <strong>{{ audit.action }}</strong>
                  <StatusBadge :status="audit.result" />
                </div>
                <p class="helper">{{ audit.reviewerName }} · {{ formatDate(audit.createdAt) }} · {{ audit.remark || '' }}</p>
              </div>
            </article>
          </div>
          <EmptyState v-if="!orders.length && !audits.length" title="暂无记录" description="当前没有订单和审核记录。" />
        </section>
      </section>
    </div>
  `,
  setup() {
    const summary = ref({
      pendingTutorProfiles: 0,
      openDemands: 0,
      submittedApplications: 0,
      activeOrders: 0
    });
    const profiles = ref([]);
    const demands = ref([]);
    const applications = ref([]);
    const orders = ref([]);
    const audits = ref([]);
    const remarks = reactive({});

    function seedRemarks(prefix, rows) {
      rows.forEach(row => {
        remarks[`${prefix}-${row.id}`] = row.reviewRemark || row.remark || '';
      });
    }

    async function load() {
      try {
        const [dashboard, profileRows, demandRows, applicationRows, orderRows, auditRows] = await execute(() => Promise.all([
          api.dashboard(),
          api.adminProfiles(),
          api.adminDemands(),
          api.adminApplications(),
          api.adminOrders(),
          api.adminAudits()
        ]));

        summary.value = dashboard;
        profiles.value = profileRows;
        demands.value = demandRows;
        applications.value = applicationRows;
        orders.value = orderRows;
        audits.value = auditRows;
        seedRemarks('profile', profileRows);
        seedRemarks('demand', demandRows);
        seedRemarks('application', applicationRows);
      } catch {
        profiles.value = [];
        demands.value = [];
        applications.value = [];
        orders.value = [];
        audits.value = [];
      }
    }

    async function auditProfile(profileId, approved) {
      try {
        await execute(() => api.auditProfile(state.user.id, profileId, {
          approved,
          remark: remarks[`profile-${profileId}`] || '审核处理'
        }), '教员资料审核已处理。');
        await load();
      } catch {
        // handled globally
      }
    }

    async function auditDemand(demandId, approved) {
      try {
        await execute(() => api.auditDemand(state.user.id, demandId, {
          approved,
          remark: remarks[`demand-${demandId}`] || '审核处理'
        }), '家教需求审核已处理。');
        await load();
      } catch {
        // handled globally
      }
    }

    async function reviewApplication(applicationId, approved) {
      try {
        await execute(() => api.reviewApplication(state.user.id, applicationId, {
          approved,
          remark: remarks[`application-${applicationId}`] || '审核处理'
        }), '接单申请审核已处理。');
        await load();
      } catch {
        // handled globally
      }
    }

    const metrics = computed(() => [
      { label: '待审资料', value: summary.value.pendingTutorProfiles || 0 },
      { label: '开放需求', value: summary.value.openDemands || 0 },
      { label: '待审申请', value: summary.value.submittedApplications || 0 },
      { label: '进行中订单', value: summary.value.activeOrders || 0 }
    ]);

    onMounted(load);

    return {
      applications,
      auditDemand,
      auditProfile,
      audits,
      demands,
      formatDate,
      metrics,
      orders,
      profiles,
      remarks,
      reviewApplication,
      state
    };
  }
};

const AppShell = {
  template: `
    <div>
      <div class="site-frame">
        <header class="site-header">
          <div class="nav-row">
            <router-link class="brand" to="/">
              <span class="brand-mark">NH</span>
              <span><strong>南华家教</strong><small>严选家教服务</small></span>
            </router-link>
            <nav class="main-nav" aria-label="主要导航" v-if="navigation.length">
              <router-link v-for="item in navigation" :key="item.path" :to="item.path">{{ item.label }}</router-link>
            </nav>
            <div class="header-actions" v-if="state.user">
              <span>{{ state.user.displayName }} · {{ roleText[state.user.role] || state.user.role }}</span>
              <button class="button-outline" type="button" @click="signOut">退出</button>
            </div>
            <div class="header-actions" v-else>
              <router-link class="button-outline" to="/login">登录</router-link>
              <router-link class="button" to="/register">注册</router-link>
            </div>
          </div>
        </header>

        <main class="page">
          <div class="alert-row" v-if="state.notice || state.error">
            <div v-if="state.notice" class="alert alert-box">
              <span>{{ state.notice }}</span>
              <button class="text-button" type="button" @click="clearMessages">关闭</button>
            </div>
            <div v-if="state.error" class="alert error alert-box">
              <span>{{ state.error }}</span>
              <button class="text-button" type="button" @click="clearMessages">关闭</button>
            </div>
          </div>
          <router-view />
        </main>
      </div>

      <footer class="site-footer">
        <div><strong>南华家教</strong><p>让每一次家教匹配都有清晰流程和可靠跟进。</p></div>
        <div class="footer-meta"><span>家长服务</span><span>教员入驻</span><span>平台审核</span></div>
      </footer>

      <div v-if="state.loading" class="loading-mask">正在处理请求...</div>
    </div>
  `,
  setup() {
    const router = useRouter();
    const navigation = computed(() => {
      if (!state.user) return [];
      return [
        { path: workspacePath(state.user), label: '工作台' },
        { path: '/demands', label: '需求大厅' },
        { path: '/tutors', label: '教员库' }
      ];
    });

    function signOut() {
      logoutUser();
      router.push('/login');
    }

    return {
      clearMessages,
      navigation,
      roleText,
      signOut,
      state
    };
  }
};

const routes = [
  {
    path: '/',
    redirect: () => workspacePath(state.user)
  },
  {
    path: '/login',
    component: LoginPage,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    component: RegisterPage,
    meta: { guestOnly: true }
  },
  {
    path: '/demands',
    component: DemandListPage
  },
  {
    path: '/demands/:id',
    component: DemandDetailPage
  },
  {
    path: '/tutors',
    component: TutorListPage
  },
  {
    path: '/tutors/:id',
    component: TutorDetailPage
  },
  {
    path: '/tutor-users/:id/profile',
    component: TutorDetailPage
  },
  {
    path: '/parent',
    component: ParentPage,
    meta: { role: 'PARENT' }
  },
  {
    path: '/tutor',
    component: TutorPage,
    meta: { role: 'TUTOR' }
  },
  {
    path: '/admin',
    component: AdminPage,
    meta: { role: 'ADMIN' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  if (to.meta.guestOnly && state.user) {
    return workspacePath(state.user);
  }

  if (to.meta.role && !state.user) {
    flashNotice('请先登录后进入对应工作台。');
    return '/login';
  }

  if (to.meta.role && state.user?.role !== to.meta.role) {
    flashNotice('已为你切换到对应角色工作台。');
    return workspacePath(state.user);
  }

  return true;
});

const app = createApp(AppShell);
app.component('StatusBadge', StatusBadge);
app.component('EmptyState', EmptyState);
app.component('DemandCard', DemandCard);
app.component('TutorCard', TutorCard);
app.use(router);
app.mount('#app');
