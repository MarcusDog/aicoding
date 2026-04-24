package com.lidacollege.volunteer.modules.admin.dto;

public record StudentSaveRequest(
    String studentNo,
    String name,
    String gender,
    String collegeName,
    String majorName,
    String className,
    String phone,
    String email,
    String avatarUrl,
    String remark,
    String password
) {
}
