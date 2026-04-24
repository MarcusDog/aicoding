package com.lidacollege.volunteer.modules.student.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record SignCodeRequest(
    @NotNull Long activityId,
    @NotBlank String code
) {
}
