package com.nanhua.tutor.web;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.forwardedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.nio.charset.StandardCharsets;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.util.StreamUtils;

@SpringBootTest
@AutoConfigureMockMvc
class StaticFrontendTest {
  @Autowired
  private MockMvc mockMvc;

  @Test
  void servesVueFrontendAssetsFromSpringBoot() throws Exception {
    mockMvc.perform(get("/index.html"))
        .andExpect(status().isOk())
        .andExpect(content().string(containsString("vendor/vue.global.prod.js")))
        .andExpect(content().string(containsString("vendor/vue-router.global.prod.js")))
        .andExpect(content().string(containsString("app/main.js")))
        .andExpect(content().string(containsString("app/styles.css")))
        .andExpect(content().string(containsString("lang=\"zh-CN\"")));
  }

  @Test
  void forwardsFrontendRoutesToStaticIndex() throws Exception {
    mockMvc.perform(get("/"))
        .andExpect(status().isOk())
        .andExpect(forwardedUrl("/index.html"));

    mockMvc.perform(get("/admin"))
        .andExpect(status().isOk())
        .andExpect(forwardedUrl("/index.html"));
  }

  @Test
  void staticFrontendUsesVueRouterEntry() throws Exception {
    String appScript = StreamUtils.copyToString(
        new ClassPathResource("static/app/main.js").getInputStream(),
        StandardCharsets.UTF_8
    );

    org.assertj.core.api.Assertions.assertThat(appScript)
        .contains("window.Vue")
        .contains("createRouter")
        .contains("router.beforeEach");
  }

  @Test
  void staticFrontendDoesNotExposeOutdatedTechnicalCopy() throws Exception {
    String indexHtml = StreamUtils.copyToString(
        new ClassPathResource("static/index.html").getInputStream(),
        StandardCharsets.UTF_8
    );
    String appScript = StreamUtils.copyToString(
        new ClassPathResource("static/app/main.js").getInputStream(),
        StandardCharsets.UTF_8
    );

    org.assertj.core.api.Assertions.assertThat(indexHtml)
        .doesNotContain("/assets/app.js")
        .doesNotContain("/assets/styles.css");

    org.assertj.core.api.Assertions.assertThat(appScript)
        .doesNotContain("衡阳地区家教供需发布、教员求职与平台审核系统")
        .doesNotContain("前端为 Spring Boot 静态资源")
        .doesNotContain("Spring Boot + 原生 JavaScript");
  }
}
