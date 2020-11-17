package org.confeti.db.dao.speaker;

import com.datastax.dse.driver.api.mapper.reactive.MappedReactiveResultSet;
import com.datastax.oss.driver.api.mapper.annotations.Dao;
import com.datastax.oss.driver.api.mapper.annotations.Select;
import org.confeti.db.dao.BaseDao;
import org.confeti.db.model.speaker.SpeakerByConferenceEntity;

@Dao
public interface SpeakerByConferenceDao extends BaseDao<SpeakerByConferenceEntity> {

    @Select
    MappedReactiveResultSet<SpeakerByConferenceEntity> findByConferenceName(String conferenceName);

    @Select
    MappedReactiveResultSet<SpeakerByConferenceEntity> findByConferenceNameForYear(String conferenceName, Integer year);
}
