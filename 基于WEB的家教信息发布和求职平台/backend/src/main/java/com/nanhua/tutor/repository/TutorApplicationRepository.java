package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.ApplicationStatus;
import com.nanhua.tutor.domain.TutorApplication;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.UserAccount;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TutorApplicationRepository extends JpaRepository<TutorApplication, Long> {
  boolean existsByDemandAndTutor(TutorDemand demand, UserAccount tutor);

  List<TutorApplication> findByTutorOrderByCreatedAtDesc(UserAccount tutor);

  List<TutorApplication> findByDemandOrderByCreatedAtDesc(TutorDemand demand);

  long countByStatus(ApplicationStatus status);
}
