package com.nanhua.tutor.repository;

import com.nanhua.tutor.domain.UserAccount;
import com.nanhua.tutor.domain.UserRole;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserAccountRepository extends JpaRepository<UserAccount, Long> {
  Optional<UserAccount> findByUsername(String username);

  long countByRole(UserRole role);
}
