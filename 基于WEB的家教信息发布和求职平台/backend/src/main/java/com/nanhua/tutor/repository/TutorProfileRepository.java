package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.AuditStatus;
import com.nanhua.tutor.domain.TutorProfile;
import com.nanhua.tutor.domain.UserAccount;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TutorProfileRepository extends JpaRepository<TutorProfile, Long> {
  Optional<TutorProfile> findByUser(UserAccount user);

  long countByStatus(AuditStatus status);
}
