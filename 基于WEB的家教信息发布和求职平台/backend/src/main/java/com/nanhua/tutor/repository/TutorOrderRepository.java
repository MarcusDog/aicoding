package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.OrderStatus;
import com.nanhua.tutor.domain.TutorOrder;
import com.nanhua.tutor.domain.UserAccount;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TutorOrderRepository extends JpaRepository<TutorOrder, Long> {
  List<TutorOrder> findByParentOrderByCreatedAtDesc(UserAccount parent);

  List<TutorOrder> findByTutorOrderByCreatedAtDesc(UserAccount tutor);

  long countByStatus(OrderStatus status);
}
