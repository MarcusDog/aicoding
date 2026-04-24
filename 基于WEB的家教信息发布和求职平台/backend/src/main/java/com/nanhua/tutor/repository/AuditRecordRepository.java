package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.AuditRecord;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AuditRecordRepository extends JpaRepository<AuditRecord, Long> {
  List<AuditRecord> findTop20ByOrderByCreatedAtDesc();
}
