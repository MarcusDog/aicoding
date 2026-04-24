package com.lidacollege.volunteer.modules.student.dto;

public record StudentProfileUpdateRequest(
    String phone,
    String email,
    String avatarUrl,
    String remark
) {
}
