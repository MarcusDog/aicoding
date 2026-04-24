package com.lidacollege.volunteer.modules.admin.dto;

public record AdminSaveRequest(
    String adminNo,
    String name,
    String phone,
    String email,
    String titleName,
    String password
) {
}
