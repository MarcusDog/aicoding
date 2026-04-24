package com.nanhua.tutor.service;

import com.nanhua.tutor.domain.TutorProfile;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Set;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

@Service
public class TutorResumeStorageService {
  private static final Set<String> ALLOWED_EXTENSIONS = Set.of("pdf", "doc", "docx", "txt");
  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

  private final Path rootDir;

  public TutorResumeStorageService(@Value("${app.storage.resume-dir:uploads/resumes}") String rootDir) {
    this.rootDir = Paths.get(rootDir).toAbsolutePath().normalize();
  }

  public StoredResume store(TutorProfile profile, MultipartFile file) {
    if (file == null || file.isEmpty()) {
      throw new BusinessException("请先选择简历文件");
    }

    String originalFilename = StringUtils.cleanPath(file.getOriginalFilename() == null ? "resume.txt" : file.getOriginalFilename());
    String extension = extensionOf(originalFilename);
    if (!ALLOWED_EXTENSIONS.contains(extension)) {
      throw new BusinessException("仅支持上传 pdf、doc、docx、txt 格式的简历");
    }

    try {
      Path profileDir = rootDir.resolve(String.valueOf(profile.getId()));
      Files.createDirectories(profileDir);
      String storedFilename = FORMATTER.format(LocalDateTime.now()) + "-" + originalFilename.replaceAll("[^a-zA-Z0-9._-]", "_");
      Path storedPath = profileDir.resolve(storedFilename).normalize();
      try (InputStream inputStream = file.getInputStream()) {
        Files.copy(inputStream, storedPath, StandardCopyOption.REPLACE_EXISTING);
      }
      return new StoredResume(
          originalFilename,
          storedPath.toString(),
          file.getContentType() == null ? "application/octet-stream" : file.getContentType(),
          file.getSize()
      );
    } catch (IOException exception) {
      throw new BusinessException("简历文件保存失败");
    }
  }

  public Resource loadAsResource(TutorProfile profile) {
    if (profile.getResumeFilePath() == null || profile.getResumeFilePath().isBlank()) {
      throw new BusinessException("简历附件不存在");
    }

    try {
      Resource resource = new UrlResource(Path.of(profile.getResumeFilePath()).toUri());
      if (!resource.exists()) {
        throw new BusinessException("简历附件不存在");
      }
      return resource;
    } catch (IOException exception) {
      throw new BusinessException("简历附件读取失败");
    }
  }

  private String extensionOf(String filename) {
    int index = filename.lastIndexOf('.');
    if (index < 0 || index == filename.length() - 1) {
      return "";
    }
    return filename.substring(index + 1).toLowerCase();
  }

  public record StoredResume(String fileName, String filePath, String contentType, long fileSize) {
  }
}
