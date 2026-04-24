package com.lidacollege.volunteer.modules.admin.dto;

public record NoticeSaveRequest(
    String title,
    String content,
    String attachmentUrl
) {
}
