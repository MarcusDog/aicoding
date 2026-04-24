package com.lidacollege.volunteer.modules.file.controller;

import com.lidacollege.volunteer.common.api.ApiResponse;
import com.lidacollege.volunteer.modules.file.service.FileStorageService;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final FileStorageService fileStorageService;

    @PostMapping("/upload/avatar")
    public ApiResponse<Map<String, String>> uploadAvatar(@RequestParam("file") MultipartFile file) {
        return ApiResponse.ok(Map.of("url", fileStorageService.save(file, "avatar")));
    }

    @PostMapping("/upload/activity-cover")
    public ApiResponse<Map<String, String>> uploadActivityCover(@RequestParam("file") MultipartFile file) {
        return ApiResponse.ok(Map.of("url", fileStorageService.save(file, "activity-cover")));
    }

    @PostMapping("/upload/activity-attachment")
    public ApiResponse<Map<String, String>> uploadActivityAttachment(@RequestParam("file") MultipartFile file) {
        return ApiResponse.ok(Map.of("url", fileStorageService.save(file, "activity-attachment")));
    }

    @PostMapping("/upload/notice-attachment")
    public ApiResponse<Map<String, String>> uploadNoticeAttachment(@RequestParam("file") MultipartFile file) {
        return ApiResponse.ok(Map.of("url", fileStorageService.save(file, "notice-attachment")));
    }
}
