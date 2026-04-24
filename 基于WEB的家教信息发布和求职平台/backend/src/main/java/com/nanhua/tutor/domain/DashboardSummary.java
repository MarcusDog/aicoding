package com.nanhua.tutor.domain;

public record DashboardSummary(
    long parents,
    long tutors,
    long admins,
    long openDemands,
    long pendingTutorProfiles,
    long submittedApplications,
    long activeOrders
) {
}
