package com.lidacollege.volunteer.modules.student.dto;

import jakarta.validation.constraints.NotBlank;

public record CancelSignupRequest(
    @NotBlank String cancelReason
) {
}
