-- Add session_id column to refresh_tokens table
create table if not exists auth.sessions (
    id uuid not null,
    user_id uuid not null,
    created_at timestamptz null,
    updated_at timestamptz null,
    constraint sessions_pkey primary key (id),
    constraint sessions_user_id_fkey foreign key (user_id) references auth.users(id) on delete cascade
);
comment on table auth.sessions is 'Auth: Stores session data associated to a user.';
