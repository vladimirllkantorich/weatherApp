import streamlit as st
import pandas as pd
import plotly.express as px


def _fmt_top_cities(top) -> str:
    if not top:
        return ""
    parts = []
    for item in top:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            city, cnt = item
            parts.append(f"{city}: {cnt}")
        else:
            parts.append(str(item))
    return ", ".join(parts)


def render_admin_stats(store, actor) -> None:
    stats = store.all_stats(actor)

    st.subheader("Admin — all users statistics")
    st.metric("Total requests (all users)", stats.get("total_requests_all_users", 0))
    st.divider()

    top = stats.get("top_cities_all_users", [])
    if top:
        df_top = pd.DataFrame(top, columns=["city", "requests"])
        fig = px.bar(df_top, x="city", y="requests", title="Top cities (all users)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No city requests yet.")

    home = stats.get("home_cities_distribution", [])
    if home:
        df_home = pd.DataFrame(home, columns=["home_city", "users"])
        fig = px.bar(df_home, x="home_city", y="users", title="Home cities distribution")
        st.plotly_chart(fig, use_container_width=True)

    per_user = stats.get("per_user", [])
    if per_user:
        df_users = pd.DataFrame(per_user)

        if "top_cities" in df_users.columns:
            df_users["top_cities"] = df_users["top_cities"].apply(_fmt_top_cities)

        st.divider()
        st.subheader("Per-user table")
        st.dataframe(df_users, use_container_width=True)

        if "total_requests" in df_users.columns:
            xcol = "nickname" if "nickname" in df_users.columns else df_users.index
            fig = px.bar(
                df_users.sort_values("total_requests", ascending=False),
                x=xcol,
                y="total_requests",
                title="Total requests by user",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Delete user")

    users = sorted(store._users.keys())
    users = [u for u in users if u != actor.nickname]

    if users:
        nick_to_delete = st.selectbox("Select user", users, key="admin_delete_user")
        confirm = st.checkbox("I understand this will permanently delete the user", key="admin_delete_confirm")

        if st.button("Delete selected user", disabled=not confirm):
            try:
                store.delete_user(nick_to_delete, actor)
                st.success(f"Deleted: {nick_to_delete}")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    else:
        st.info("No users to delete.")

