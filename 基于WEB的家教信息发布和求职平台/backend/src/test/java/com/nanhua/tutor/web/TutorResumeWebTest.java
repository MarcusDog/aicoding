package com.nanhua.tutor.web;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.nanhua.tutor.domain.UserAccount;
import com.nanhua.tutor.domain.UserRole;
import com.nanhua.tutor.service.TutorPlatformService;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class TutorResumeWebTest {
  @Autowired
  private MockMvc mockMvc;

  @Autowired
  private TutorPlatformService service;

  @Test
  void tutorCanUploadAndDownloadResumeFile() throws Exception {
    UserAccount tutor = service.registerUser("resume_case1", "123456", "附件教员", "18880000001", UserRole.TUTOR);
    var profile = service.submitTutorProfile(
        tutor.getId(),
        "南华大学",
        "数学与应用数学",
        "数学",
        "擅长基础巩固",
        2,
        "线上",
        "提供阶段学习反馈"
    );

    MockMultipartFile file = new MockMultipartFile(
        "file",
        "resume-case1.txt",
        "text/plain",
        "这是教员的简历附件".getBytes()
    );

    mockMvc.perform(multipart("/api/tutors/{tutorId}/profile/resume-file", tutor.getId()).file(file))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.resumeFileName").value("resume-case1.txt"))
        .andExpect(jsonPath("$.resumeFileDownloadUrl").value(containsString("/api/catalog/tutors/" + profile.getId() + "/resume-file")));

    mockMvc.perform(get("/api/catalog/tutors/{profileId}/resume-file", profile.getId()))
        .andExpect(status().isOk())
        .andExpect(header().string("Content-Disposition", containsString("resume-case1.txt")))
        .andExpect(content().bytes("这是教员的简历附件".getBytes(StandardCharsets.UTF_8)));
  }
}
