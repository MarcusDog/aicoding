package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.DemandStatus;
import com.nanhua.tutor.domain.TutorDemand;
import com.nanhua.tutor.domain.UserAccount;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TutorDemandRepository extends JpaRepository<TutorDemand, Long> {
  List<TutorDemand> findByStatusOrderByCreatedAtDesc(DemandStatus status);

  List<TutorDemand> findByParentOrderByCreatedAtDesc(UserAccount parent);

  long countByStatus(DemandStatus status);
}
